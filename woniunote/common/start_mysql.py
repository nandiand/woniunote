import time
from pywinauto import *  # 导包
from pynput.mouse import Button,Controller as mouse_cl

mouse = mouse_cl()
def start_mysql():  # 定义一个自动化任务的函数
    app = Application().start('C:\Program Files\MySQL\MySQL Workbench 8.0\MySQLWorkbench.exe')  # 实例化一个对象，并启动指定的应用程序，start参数也可写入路径
    time.sleep(2)
    mouse.position = (500, 1300)
    mouse.press(Button.left)
    mouse.release(Button.left)
    time.sleep(1)
    win = app['MySQL Workbench']
    win.minimize()


