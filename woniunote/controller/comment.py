
from flask import Blueprint, request, session, jsonify
from module.article import Article
from module.comment import Comment
from module.credit import Credit
from module.opinion import Opinion
from module.users import Users

comment = Blueprint('comment',__name__)


@comment.before_request
def before_comment():
    url = request.path
    pass_list = ['/comment','/reply']
    if url not in pass_list:
        pass
    elif url in pass_list and session.get('islogin') is None or session.get('islogin') != 'true':
        return 'not-login'

@comment.route('/comment',methods=['POST'])
def add():
    articleid = request.form.get('articleid')
    content = request.form.get('content').strip()
    ipaddr = request.remote_addr
    #对评论内容进行简单检验
    if len(content) < 5 or len(content) > 1000:
        return 'content-invalid'
    comment = Comment()
    if not comment.check_limit_per_5():
        try:
            comment.insert_comment(articleid,content,ipaddr)
            #评论成功后，更新积分明细和剩余积分，及文章回复数量
            Credit().insert_detail(type='添加评论',target=articleid,credit=2)
            Users().updata_credit(2)
            Article().update_replycount(articleid)
            return 'add-pass'
        except:
            return 'add-fail'
    else:
        return 'add-limit'

@comment.route('/reply',methods=['POST'])
def reply():
    articleid = request.form.get('articleid')
    commentid = request.form.get('commentid')
    content = request.form.get('content').strip()
    ipaddr = request.remote_addr
    # 对评论内容进行简单检验
    if len(content) < 5 or len(content) > 1000:
        return 'content-invalid'
    comment = Comment()
    if not comment.check_limit_per_5():
        try:
            comment.insert_reply(articleid=articleid,commentid=commentid,content=content, ipaddr=ipaddr)
            # 评论成功后，更新积分明细和剩余积分，及文章回复数量
            Credit().insert_detail(type='回复评论', target=articleid, credit=2)
            Users().updata_credit(2)
            Article().update_replycount(articleid)
            return 'reply-pass'
        except:
            return 'reply-fail'
    else:
        return 'reply-limit'

#由于分页栏已经完成渲染，此接口仅根据前端的页码请求后台对应数据
@comment.route('/comment/<int:articleid>-<int:page>')
def comment_page(articleid,page):
    start = (page-1)*10
    comment = Comment()
    list = comment.get_comment_user_list(articleid,start,10)
    return jsonify(list)

#接受用户点赞请求
@comment.route('/opinion',methods=['POST'])
def do_opinion():
    commentid =request.form.get('commentid')
    type = int(request.form.get('type'))
    ipaddr = request.remote_addr
    #判断是否已经点赞
    opinion = Opinion()
    is_checked = opinion.check_opinion(commentid,ipaddr)
    if is_checked:
        return 'already-opinion'   #已经点赞，不能再赞
    else:
        opinion.insert_opinion(commentid,type,ipaddr)
        Comment().update_agree_oppose(commentid,type)
        return 'opinion-pass'

#接受用户隐藏请求,自己写的
@comment.route('/hide/<int:commentid>',methods=['DELETE'])
def do_hide():
    commentid = request.form.get('commentid')
    print(commentid)
    hide = Comment()
    result = hide.hide_comment(commentid)
    if result:
        return 'hide-pass'
    else:
        return 'hide-limit'