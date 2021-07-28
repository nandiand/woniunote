import math
from flask import Blueprint, abort, render_template, request, session

from common.utility import parse_image_url, generate_thumb
from module.article import Article
from module.comment import Comment
from module.credit import Credit
from module.favorite import Favorite
from module.users import Users

article = Blueprint('article',__name__)

@article.route('/article/<int:articleid>')
def read(articleid):
    try:
        #result数据格式为：（Article,'nickname')
        result = Article().find_by_id(articleid)
        if result is None:
            abort(404)
    except:
        abort(500)
    dict={}
    for k,v in result[0].__dict__.items():
        if not k.startswith('_sa_instance_state'):
            dict[k] = v
    dict['nickname'] = result.nickname
    #如果已经已经消耗积分，且文章不需要积分,则不在截取文章内容，
    payed = Credit().check_payed_article(articleid)
    credit = Article().find_credit_by_id(articleid)
    position = 0
    if credit > 0:
        if not payed:
            content = dict['content']
            temp = content[0:int(len(content)/3)]
            position = temp.rindex('</p>') + 4   #切断之后，向前找到最近一个P闭合标签作为最终截取点
            dict['content'] = temp[0:position]
    Article().update_read_count(articleid)  #阅读次数+1
    is_favorited = Favorite().check_favorite(articleid)
    #获取当前文章的上一篇和下一篇
    prev_next = Article().find_prev_next_by_id(articleid)
    #显示当前文章对应的评论
    #comment_user = Comment().find_limit_with_user(articleid,0,50)    #这行不用了，重构为下面comment_list了
    #显示原始评论和回复评论
    comment_list = Comment().get_comment_user_list(articleid,0,10)
    #获取原始评论总数
    count = Comment().get_count_by_article(articleid)
    total = math.ceil(count/10)
    # print(count,total)
    return render_template('article-user.html',article=dict,position=position,payed=payed,
                           is_favorited=is_favorited,prev_next=prev_next,comment_list=comment_list,total=total)

@article.route('/readall',methods=['POST'])
def read_all():
    position = int(request.form.get('position'))
    articleid = request.form.get('articleid')
    article = Article()
    result = article.find_by_id(articleid)
    content = result[0].content[position:]
    #如果已经消耗积分，则不再扣除
    payed = Credit().check_payed_article(articleid)
    if not payed:
        #添加积分明细
        Credit().insert_detail(type='阅读文章',target=articleid,credit=-1*result[0].credit)
        #减少用户表的剩余积分
        Users().updata_credit(credit=-1*result[0].credit)
    return content

# @article.route('/prepost')
# def pre_post():
#     return render_template('post-user.html')

#发布文章
@article.route('/article',methods=['POST'])
def add_article():
    headline = request.form.get('headline')
    content = request.form.get('content')
    type = int(request.form.get('type'))
    credit = int(request.form.get('credit'))
    drafted = int(request.form.get('drafted'))
    checked = int(request.form.get('checked'))
    articleid = int(request.form.get('articleid'))

    if session.get('userid') is None:
        print(session.get('userid'))
        return 'perm-denied'
    else:
        user = Users().find_by_userid(session.get('userid'))
        if user.role == 'editor':
            url_list = parse_image_url(content)
            if len(url_list) >0:
                thumbname = generate_thumb(url_list)
            else:
                thumbname = '%d.png' % type

            article = Article()
            #再判断articleid是否为0，如果为零则表示时新数据
            if articleid == 0:
                try:
                    id = article.insert_article(type=type,headline=headline,content=content,credit=credit,
                                                thumbnail=thumbname,drafted=drafted,checked=checked)
                    return str(id)
                except Exception as e:
                    return 'post-fail'
            else:
                #如果时已经添加过的文章
                try:
                    id = article.update_article(articleid=articleid,type=type,headline=headline,content=content,
                                                credit=credit,thumbnail=thumbname,drafted=drafted,checked=checked)
                    return str(id)
                except:
                    return 'post-fail'

        #如果角色不是editor，只能投稿
        elif checked == 1:
            return 'perm-denied'
        else:
            return 'perm-denied'


