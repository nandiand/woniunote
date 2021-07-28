import os
import time

from flask import Blueprint, request, render_template, jsonify

from common.utility import compress_image

ueditor = Blueprint('ueditor',__name__)

@ueditor.route('/uedit',methods=['GET','POST'])
def uedit():
    param = request.args.get('action')
    if request.method == 'GET' and param == 'config':
        return render_template('config.json')

    #构造上传图片的接口
    elif request.method == 'POST' and request.args.get('action') == 'uploadimage':
        f = request.files['upfile']      #获取前端图片文件数据
        filename = f.filename
        #为上传的图片生成统一的文件名
        suffix = filename.split('.')[-1]
        newname = time.strftime('%Y%m%d_%H%M%S.'+suffix)
        f.save('./resource/upload/' + newname)  #保存图片到upload目录
        #对图片进行压缩
        source = dest ='./resource/upload/' + newname
        compress_image(source,dest,1200)
        result = {}
        result['state'] = 'SUCCESS'
        result['url'] = f"/upload/{newname}"
        result['title'] = filename
        result['original'] = filename
        return jsonify(result)

    #列出图片给前端浏览
    elif request.method == 'GET' and param == 'listimage':
        list= []
        filelist = os.listdir('./resource/upload')
        for filename in filelist:
            if filename.lower().endswith('.png') or filename.lower().endswith('.jpg'):
                list.append({'url':'/upload/%s' % filename})
        #根据listimage接口规则构建响应数据
        result = {}
        result['state'] = 'SUCCESS'
        result['list'] = list
        result['start'] = 0
        result['total'] = 50
        return jsonify(result)
