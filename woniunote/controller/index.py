
#搭建首页控制器
import hashlib
import math
from flask import Blueprint, render_template, abort, jsonify, session, request
from module.article import Article

#定义一个blueprint的index模块名称
from module.users import Users

index = Blueprint('index',__name__)

@index.route('/')
def home():
    article = Article()
    result = article.find_limit_with_users(0,10)
    total = math.ceil(article.get_total_count() / 10)  # 总文章数除以10得到页数，向上取整
    return render_template('index.html',result=result,total=total,page=1)

@index.route('/page/<int:page>')
def paginate(page):
    article = Article()
    start = (page-1)*10
    result = article.find_limit_with_users(start,10)
    total = math.ceil(article.get_total_count()/10)   #总文章数除以10得到页数，向上取整
    return render_template('index.html',result=result,total=total,page=page)

@index.route('/type/<int:type>-<int:page>')
def classify(type,page):
    article = Article()
    start = (page - 1) * 10
    result = article.find_by_type(type, start, 10)
    total = math.ceil(article.get_count_by_type(type)/10)
    return render_template('type.html',result=result,page=page,total=total,type=type)

@index.route('/search/<int:page>-<keyword>')
def search(page,keyword):
    keyword = keyword.strip()
    if keyword is None or keyword=='' or '%' in keyword or len(keyword) > 10:
        abort(404)
    start = (page-1)*10
    article = Article()
    result = article.find_by_headline(keyword, start, 10)
    total = math.ceil(article.get_count_by_headline(keyword) / 10)  # 总文章数除以10得到页数，向上取整
    return render_template('search.html', result=result, total=total, page=page,keyword=keyword)

@index.route('/recommend')
def recommend():
    article = Article()
    last, most, recommended = article.find_last_most_recommended()
    return jsonify(last,most,recommended)