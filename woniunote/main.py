
from builtins import ord
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
import pymysql


pymysql.install_as_MySQLdb()

#/表示设置静态文件默认路径，在前端页面就可以使用简化绝对路径
app = Flask(__name__,template_folder='template',static_url_path='/',static_folder='resource')
#生成随机数种子，用于产生sessionID
app.config['SECRET_KEY'] = os.urandom(24)
#使用与flask与集成的方式处理sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:970713@localhost:3306/woniunote?charset=utf8'
#True表示跟踪数据库的修改，及时发送信号，但消耗性能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#实例化db对象
db = SQLAlchemy(app)

#定义404错误页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error-404.html')

#定义500错误页面
@app.errorhandler(500)
def server_error(e):
    return render_template('error-500.html')

#定义全局拦截器实现自动登录
@app.before_request
def before():
    url = request.path
    pass_list = ['/user','/login','/logout']
    if url in pass_list or url.endswith('.js') or url.endswith('.css') or url.endswith('.png'):
        pass
    elif session.get('islogin') is None:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if username != None and password != None:
            user = Users()
            password = hashlib.md5(password.encode()).hexdigest()
            result = user.find_by_username(username)
            if len(result) == 1 and result[0].password == password:
                session['islogin'] = 'true'
                session['userid'] = result[0].userid
                session['username'] = username
                session['nickname'] = result[0].nickname
                session['role'] = result[0].role

#定义文章类型函数，供模板页面调用,context_processor这是jinja2提供的上下文处理器
@app.context_processor
def gettype():
    type = {
        '1':'PHP开发',
        '2':'Java开发',
        '3':'Python开发',
        '4':'Web前端',
        '5':'测试开发',
        '6':'数据科学',
        '7':'网络安全',
        '8':'蜗牛杂谈'
    }
    return dict(article_type=type)

#通过自定义过滤器来重构truncate
# 因特殊需要，对内置过滤器进行重写
# 中文定义为1个字符，英文定义为0.5字符
# 遍历整个字符串，获取到每一个字符的ASCII码，如果在128或256以内，则认为是英文，否则认为是中文
# 在一个项目中，如果第三方库的源代码无法满足需求，尽量自定义函数/方法来解决，而不是直接修改库的源代码，因为这样项目无法移植，别人电脑的库没改
def mytruncate(s,length,end='...'):
    count = 0
    new = ''
    for c in s:
        new += c  # 每循环一次，将一个字符添加到new字符串后面
        if ord(c) <= 128:
            count += 0.5
        else:
            count += 1
        if count > length:
            break
    return new + end
#紧接着注册该过滤器,前一个truncate是前端页面调用的方法名，后一个是自定的函数名，上传,使用前端渲染就用不上了
app.jinja_env.filters.update(truncate=mytruncate)



if __name__ == '__main__':
    from controller.index import *
    app.register_blueprint(index)  # 使用Blueprint时，必须将其注册到app中

    from controller.user import *
    app.register_blueprint(user)  # 使用Blueprint时，必须将其注册到app中

    from controller.article import *
    app.register_blueprint(article)  # 使用Blueprint时，必须将其注册到app中

    from controller.favorite import *
    app.register_blueprint(favorite)  # 使用Blueprint时，必须将其注册到app中

    from controller.comment import *
    app.register_blueprint(comment)  # 使用Blueprint时，必须将其注册到app中

    from controller.ueditor import *
    app.register_blueprint(ueditor)  # 使用Blueprint时，必须将其注册到app中

    from controller.admin import *
    app.register_blueprint(admin)  # 使用Blueprint时，必须将其注册到app中

    from controller.ucenter import *
    app.register_blueprint(ucenter)  # 使用Blueprint时，必须将其注册到app中

    app.run(debug=True)