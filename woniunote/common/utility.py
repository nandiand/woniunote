
####用验证码验证
import string
import time
from io import BytesIO
import random

from PIL import Image, ImageFont, ImageDraw

class ImageCode:
    #生成用于绘制字符串的随机颜色
    def rand_color(self):
        red = random.randint(0,255)
        green = random.randint(0,255)
        blue = random.randint(0,255)
        return red,green,blue

    #生成4位随机字符串
    def gen_text(self):
        #sample用于从一个大的列表或字符串中随机取得N个字符，来构建一个子列表
        list = random.sample(string.ascii_letters+string.digits,5)
        return ''.join(list)

    #画一些干扰线，其中draw为pil中的imagedraw对象
    def draw_lines(self,draw,num,width,height):
        for num in range(num):
            x1 = random.randint(0,width/2)
            y1 = random.randint(0,height/2)
            x2 = random.randint(0,width)
            y2 = random.randint(height/2,height)
            draw.line(((x1,y1),(x2,y2)),fill='black',width=2)

    #绘制验证码图片
    def draw_verify_code(self):
        code = self.gen_text()
        width,height = 150,50    #设定图片大小
        #创建图片对象，并设定背景为白色
        im = Image.new('RGB',(width,height),'white')
        #选择使用合适字体及字体大小
        font = ImageFont.truetype(font='arial.ttf',size=40)
        draw = ImageDraw.Draw(im)   #新建ImageDraw对象
        #绘制字符串
        for i in range(5):
            draw.text((5+random.randint(-3,3) + 23*i, 5+random.randint(-3,3)),text=code[i],fill=self.rand_color(),font=font)
        self.draw_lines(draw,5,width,height)
        return im,code

    def get_code(self):
        image,code = self.draw_verify_code()
        buf = BytesIO()
        image.save(buf,'jpeg')
        bstring = buf.getvalue()
        return code,bstring



#####用邮箱信息验证
from smtplib import SMTP_SSL
from email.mime.text import  MIMEText
from email.header import Header

#发送qq邮箱验证码，参数为收件箱地址和随机生成的验证码
def send_email(receiver,ecode):
    sender = '蒋文刚 <632619934@qq.com>'  #你的邮箱账号和发件者签名
    #定义发送邮件内容，支持html标签和css样式
    content = f'<br/>欢迎注册蜗牛笔记博客系统账号，您的邮箱验证码为：<span style="color:red;font-size:20px;">{ecode}</span>,'\
        f'请复制到注册窗口中完成注册，感谢您的支持。<br/>'
    #实例化邮件对象，并指定邮件的关键信息
    message = MIMEText(content,'html','utf-8')
    #指定邮件的标题，同样使用utf-8编码
    message['Subject'] = Header('蜗牛笔记的注册验证码','utf-8')
    message['From'] = sender
    message['To'] = receiver
    smtpObj = SMTP_SSL('smtp.qq.com')   #建议与qq邮件服务器的连接
    #通过你的邮箱账号和获取到授权码登录qq邮箱
    smtpObj.login(user='632619934@qq.com',password='hqorhjeunathbcfe')
    #指定发件人，收件人，和邮件内容
    smtpObj.sendmail(sender,receiver,str(message))
    smtpObj.quit()

#生成6为随机字符串作为邮箱验证码
def gen_email_code():
    str = random.sample(string.ascii_letters + string.digits,6)
    return ''.join(str)

# code = gen_email_code()
# send_email('632619934@qq.com',code)
# print(code)

#单个模型类转换为标准的python list数据
def model_list(result):
    list = []
    for row in result:
        dict = {}
        for k,v in row.__dict__.items():
            if not k.startswith('_sa_instance_state'):
                dict[k] = v
        list.append(dict)
    return list

#sqlalchemy连接查询两张表的结果转换为[{},{}]
def model_join_list(result):
    list = []
    for obj1,obj2 in result:
        dict = {}
        for k1,v1 in obj1.__dict__.items():
            if not k1.startswith('_sa_instance_state'):
                if not k1 in dict:     #如果字典中存在相同的key则跳过
                    dict[k1] = v1
        for k2,v2 in obj2.__dict__.items():
            if not k2.startswith('_sa_instance_state'):
                if not k2 in dict:     #如果字典中存在相同的key则跳过
                    dict[k2] = v2
        list.append(dict)
    return list

#压缩图片，通过参数width指定压缩后的图片大小
def compress_image(source,dest,width):
    from PIL import Image
    #如果图片宽度大于1200，则调整为1200的宽度
    im = Image.open(source)
    x,y = im.size
    if  x > width:
        ys = int(y*width / x)
        xs = width
        #调整当前图片的尺寸，同时也会压缩大小
        temp = im.resize((xs,ys),Image.ANTIALIAS)
        # 将图片保存并使用80%的质量进行压缩,二次压缩
        temp.save(dest, quality=80)
    #如果图片尺寸小于指定宽度则不缩减尺寸，只压缩保存
    else:
        im.save(dest, quality=80)

#解析文章中的图片，制作缩略图
def parse_image_url(content):
    import re
    temp_list = re.findall('<img src="(.+?)"',content)  #非贪婪模式
    url_list = []
    print(url_list)
    for url in temp_list:
        #如果图片类型为gif则直接跳过，不做处理
        if url.lower().endswith('.gif'):
            continue
        url_list.append(url)
    return url_list

#远程下载指定url的图片，并保存再临时目录中
def download_image(url,dest):
    import requests
    response = requests.get(url)
    with open(dest,'wb') as file:
        file.write(response.content)

#解析列表中的图片url并生成缩略图
def generate_thumb(url_list):
    #分局url解析出文件名和域名，通常建议将第一张图片生成缩略图，先看是否存在本地图片，找到即处理
    for url in url_list:
        if url.startswith('/upload/'):
            filename = url.split('/')[-1]
            #找到本地图时进行压缩处理，设置为400宽即可
            compress_image('./resource/upload/' + filename,'./resource/thumb/' + filename,400)
            return filename
    #如果没有找到本地图片，则需要先将网上图片下载到本地，将第一张图片作为缩略图，并生成时间戳的文件名
    url = url_list[0]
    filename = url.split('/')[-1]
    suffix = filename.split('.')[-1] #获取后缀名
    thumbname = time.strftime('%Y%m%d_%H%M%S.'+suffix)
    download_image(url,'./resource/download/'+thumbname)
    compress_image('./resource/download/'+ thumbname,'./resource/thumb/'+ thumbname,400)
    return thumbname


# if __name__ == '__main__':
#     content = '''<div>asdnksgdsgndnvksiuhriekkfnn<p><img src="http://www.bossqiang.com/img/banner-1.jpg"/></p>askkshfdkjshfshgdg
#     asgdhdfhf</div>sgdhfj<img srcc="/upload/小黄人.jpg"/>'''
#     list = parse_image_url(content)
#     thumb = generate_thumb(list)
#     print(thumb)