import hashlib
import re
from flask import Blueprint, make_response, session, request, redirect
from common.utility import gen_email_code, send_email, ImageCode
from module.credit import Credit
from module.users import Users

user = Blueprint('user',__name__)

#使用图片验证码
@user.route('/vcode')
def vcode():
    code,bstring = ImageCode().get_code()
    response = make_response(bstring)
    response.headers['Content-Type'] = 'image/jpeg'
    session['vcode'] = code.lower()
    return response

#使用邮箱验证码
@user.route('/ecode',methods=['POST'])
def ecode():
    email = request.form.get('email')
    # print(email)
    if not re.match('.+@.+\..+',email):
        return 'email-invalid'
    code = gen_email_code()
    try:
        send_email(email,code)
        session['ecode'] = code   #将邮箱验证码保存在session中
        return 'send-pass'
    except:
        return 'send-fail'

#实现注册
@user.route('/user',methods=['POST'])
def register():
    user=Users()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    ecode = request.form.get('ecode').strip()
    # print(ecode,session.get('ecode'))
    #校验邮箱验证码是否正确
    if ecode != session.get('ecode'):
        return 'ecode-error'
    #验证邮箱地址的正确性和密码的有效性
    elif not re.match('.+@.+\..+',username) or len(password) <5:
        return 'up-invalid'
    #验证用户是否已经注册
    elif len(user.find_by_username(username)) > 0:
        return 'user-repeated'
    else:
        #实现注册功能
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.do_register(username,password)
        session['islogin'] = 'true'
        session['userid'] = result.userid
        session['username'] = username
        session['nickname'] = result.nickname
        session['role'] = result.role
        #更新积分详情表
        Credit().insert_detail(type='用户注册',target='0',credit=50)
        return 'reg-pass'

#实现登录
@user.route('/login',methods=['POST'])
def login():
    user=Users()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    vcode = request.form.get('vcode').lower().strip()
    # print(ecode,session.get('ecode'))
    #校验图形验证码是否正确
    if vcode != session.get('vcode') :
        return 'vcode-error'
    else:
        #实现登录功能
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.find_by_username(username)
        if len(result) == 1 and result[0].password==password:
            session['islogin'] = 'true'
            session['userid'] = result[0].userid
            session['username'] = username
            session['nickname'] = result[0].nickname
            session['role'] = result[0].role
            #更新积分详情表
            Credit().insert_detail(type='正常登录',target='0',credit=1)
            user.updata_credit(1)
            #将cookie写入浏览器
            response = make_response('login-pass')
            response.set_cookie('username',username,max_age=30*24*3600)
            response.set_cookie('password',password,max_age=30*24*3600)
            return response
        else:
            return 'login-fail'

#实现注销，清空session，删除cookie,页面跳转
@user.route('/logout')
def logout():
    session.clear()
    response = make_response('注销并进行重定向',302)
    response.headers['location'] = '/'
    response.delete_cookie('username')
    response.set_cookie('password','',max_age=0)
    return response

#自动登录：第一步：利用cookie的持久化存储机制来保存用户登录信息
#        1.sessinID
#        2.利用加密机制，存储一个自定义规则的GUID
#        3.直接保存username和password（MD5），直接发送给服务器
#            1）.在登录成功后，必须将cookie写入浏览器
#            2).在接口中。从cookie中获取用户名和密码，并完成登录验证
#        第二步：利用全局拦截器实现自动登录的过程处理