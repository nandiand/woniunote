#模型类的文件尽量同表名保持一致
import time
from flask import session
from sqlalchemy import Table
from common.database import dbconnect

from common.utility import model_join_list
from module.users import Users

dbsession,md,DBase = dbconnect()

class Comment(DBase):
    __table__ = Table('comment',md,autoload=True)

    #新增一条评论
    def insert_comment(self,articleid,content,ipaddr):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        comment = Comment(userid=session.get('userid'),articleid=articleid,content=content,ipaddr=ipaddr,createtime=now,updatetime=now)
        dbsession.add(comment)
        dbsession.commit()


    #给根据文章编号查询所有评论
    def find_by_articleid(self,articleid):
        result = dbsession.query(Comment).filter_by(hidden=0,replyid=0,articleid=articleid).all()
        dbsession.close()
        return result


    #根据用户编号和日期进行查询是否已经超过每天5条限制的
    def check_limit_per_5(self):
        start = time.strftime('%Y-%m-%d 00:00:00')  #当天其实时间
        end = time.strftime('%Y-%m-%d 23:59:59')  #当天结束时间
        result = dbsession.query(Comment).filter(Comment.userid==session.get('userid'),Comment.createtime.between(start,end)).all()
        dbsession.close()
        if len(result) >= 5:
            return  True  #返回true表示今天已经不能发评论
        else:
            return False


    #查询评论与用户信息，注意评论也需要分页
    def find_limit_with_user(self,articleid,start,count):
        result = dbsession.query(Comment,Users).join(Users,Users.userid==Comment.userid)\
            .filter(Comment.articleid==articleid,Comment.hidden==0)\
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        dbsession.close()
        return result

    #新增一条回复，将原始评论的ID作为新评论的replyid字段进行关联
    def insert_reply(self,articleid,commentid,content,ipaddr):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        comment = Comment(userid=session.get('userid'), articleid=articleid, content=content, ipaddr=ipaddr,
                          replyid=commentid,createtime=now, updatetime=now)
        dbsession.add(comment)
        dbsession.commit()

    #查询原始评论与对应的用户信息，带分页参数
    def find_comment_with_user(self,articleid,start,count):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid) \
            .filter(Comment.articleid == articleid, Comment.hidden == 0,Comment.replyid==0) \
            .order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        dbsession.close()
        return result

    #查询回复评论，回复评论不需要分页
    def find_reply_with_user(self,replyid):
        result = dbsession.query(Comment, Users).join(Users, Users.userid == Comment.userid) \
            .filter(Comment.replyid == replyid,Comment.hidden==0).all()
        dbsession.close()
        return result

    #根据原始评论和回复评论生成一个关联列表
    def get_comment_user_list(self,articleid,start,count):
        result = self.find_comment_with_user(articleid,start,count)
        comment_list = model_join_list(result)
        for comment in comment_list:
            #查询原始评论对应的回复评论，并转换为列表保存到comment_list中
            result = self.find_reply_with_user(comment['commentid'])
            #为comment_list列表中的原始评论字典对象添加一个新key叫reply_list
            #用于存储当前这条评论的所有回复评论，如果无回复评论则列表值为空
            comment['reply_list'] = model_join_list(result)
        return comment_list  #将新的数据结构返回给控制器接口

    #查询某篇文章的原始评论总数量
    def get_count_by_article(self,articleid):
        count = dbsession.query(Comment).filter_by(articleid=articleid,hidden=0,replyid=0).count()
        dbsession.close()
        return count

    #更新评论表的点赞数量，包括赞和反对
    def update_agree_oppose(self,commentid,type):
        row = dbsession.query(Comment).filter_by(commentid=commentid).first()
        if type == 1:   #表示赞成
            row.agreecount += 1
        elif type == 0:
            row.opposecount += 1
        dbsession.commit()

    #隐藏评论
    def hide_comment(self,commentid):
        #如果评论已经有回复，且回复未全部隐藏，则不接受隐藏操作
        #返回fail表示不满足隐藏条件，隐藏成功返回done
        result = dbsession.query(Comment).filter_by(replyid=commentid,hidden=0).all()
        if len(result) > 0:
            return 'Fail'
        else:
            row = dbsession.query(Comment).filter_by(commentid=commentid).first()
            row.hidden = 1
            return 'True'
        dbsession.commit()





