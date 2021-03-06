import time
from flask import session
from sqlalchemy import Table
from common.database import dbconnect


dbsession,md,DBase = dbconnect()

class Opinion(DBase):
    __table__ = Table('opinion',md,autoload=True)

    #插入点赞记录
    def insert_opinion(self,commentid,type,ipaddr):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        if session.get('userid') is None:
            userid = 0
        else:
            userid = session.get('userid')
        opinion = Opinion(commentid=commentid,userid=userid,type=type,ipaddr=ipaddr,createtime=now,updatetime=now)
        dbsession.add(opinion)
        dbsession.commit()

    #检查某个用户是否已经对评论进行了点赞（含匿名用户），已点赞返回true
    def check_opinion(self,commentid,ipaddr):
        is_checked = False
        if session.get('userid') is None:   #匿名用户，也就是未登录用户
            result = dbsession.query(Opinion).filter_by(commentid=commentid,ipaddr=ipaddr).all()
            if len(result) >0:
                is_checked = True
        else:
            userid = session.get('userid')
            result = dbsession.query(Opinion).filter_by(commentid=commentid,userid=userid).all()
            if len(result) >0:
                is_checked = True
        dbsession.close()
        return is_checked