from flask import Blueprint, render_template, session

from module.favorite import Favorite

ucenter = Blueprint('ucenter',__name__)

@ucenter.before_request
def before_center():
    if session.get('islogin') != 'true' or session.get('role') == 'admin':
        return '请登录'

@ucenter.route('/ucenter')
def user_center():
    result = Favorite().find_my_favorite()
    # print(result)
    return render_template('user-center.html',result=result)

@ucenter.route('/user/favorite/<int:favoriteid>')
def user_favorite(favoriteid):
    canceled = Favorite().switch_favorite(favoriteid)
    # print(canceled)
    return str(canceled)

@ucenter.route('/user/post')
def user_post():
    return render_template('post-user.html')
