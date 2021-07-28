
#模型类的文件尽量同表名保持一致
from builtins import str
import random
from flask import session
from sqlalchemy import Table
from common.database import dbconnect

dbsession,md,DBase = dbconnect()

class Users(DBase):
    __table__ = Table('users',md,autoload=True)

    #查询用户名，可用于注册时判断用户是否已注册，也可用于登录校验
    def find_by_username(self,username):
        result = dbsession.query(Users).filter_by(username=username).all()
        dbsession.close()
        return result

    #实现注册，首次注册时用户只需要输入用户名和密码，所以只需要两个参数
    #注册时，在模型类中为其他字段尽力生成一些可用的值，虽不全面，但可用
    #通常用户在注册时不建议填太多资料，影响体验，可待用户后续逐步完善
    def do_register(self,username,password):
        nickname = username.split('@')[0]    #默认将邮箱账号作为昵称
        avatar = random.randint(1,16)   #从15张头像中随机选择一张
        user= Users(username=username,password=password,role='user',credit=50,
                    nickname=nickname,avatar=str(avatar)+'.png')
        dbsession.add(user)
        dbsession.commit()
        return user

    #修改用户剩余积分，积分为正数表示增加积分，为负数表示减少积分
    def updata_credit(self,credit):
        user = dbsession.query(Users).filter_by(userid=session.get('userid')).one()
        user.credit = int(user.credit) + credit
        dbsession.commit()
        dbsession.close()

    def find_by_userid(self,userid):
        user = dbsession.query(Users).filter_by(userid=userid).first()
        return user