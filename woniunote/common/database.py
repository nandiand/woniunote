
#将数据库操作所需的重复和每个模块控制器必要操作封装在一个文件中，供后期调用
from sqlalchemy import MetaData

def dbconnect():
    from main import db
    dbsession = db.session
    DBase = db.Model
    metadata = MetaData(bind=db.engine)
    return (dbsession,metadata,DBase)