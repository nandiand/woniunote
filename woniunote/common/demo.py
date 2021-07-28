
#图片压缩的演示代码
from PIL import Image
import os

#定义原始图片路径
source = 'D:/source.jpg'
size = int(os.path.getsize(source)/1024)
#以kb为单位获取图片大小
print ('原始图片大小为：%d KB' % size)

#调整图片大小为1000的宽度
im = Image.open(source)
width,height = im.size
print(width,height)
# if width > 1000:
#     #等比例缩放
#     height = int(height*1000/width)
# width = 1000
#调整当前图片的尺寸，同时压缩大小
dest = im.resize((1000,600),Image.ANTIALIAS)
#将图片保存并使用80%的质量进行压缩,二次压缩
dest.save('D:/new.jpg',quality=80)
size = int(os.path.getsize('D:/new.jpg')/1024)
print('压缩图片大小为：%d KB' % size)