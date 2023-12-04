# -*- coding: utf-8 -*-
# @Time : 2023/11/30 18:30
# @Author : Z
# @Email : S
# @File : MySQL_test.py
 # database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.model import *

SQLALCHEMY_DATABASE_URL = f'mysql+mysqlconnector://zzsoft:WOZFdvzLnjAK@183.134.75.201:23306/ny_model?charset=utf8&auth_plugin=mysql_native_password'
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



def query2dict(model_list):
    if isinstance(model_list,list):  #如果传入的参数是一个list类型的，说明是使用的all()的方式查询的
        if isinstance(model_list[0],db.Model):   # 这种方式是获得的整个对象  相当于 select * from table
            lst = []
            for model in model_list:
                dic = {}
                for col in model.__table__.columns:
                    dic[col.name] = getattr(model,col.name)
                lst.append(dic)
            return lst
        else:                           #这种方式获得了数据库中的个别字段  相当于select id,name from table
            lst = []
            for result in model_list:   #当以这种方式返回的时候，result中会有一个keys()的属性
                lst.append([dict(zip(result.keys, r)) for r in result])
            return lst
    else:                   #不是list,说明是用的get() 或者 first()查询的，得到的结果是一个对象
        if isinstance(model_list,db.Model):   # 这种方式是获得的整个对象  相当于 select * from table limit=1
            dic = {}
            for col in model_list.__table__.columns:
                dic[col.name] = getattr(model_list,col.name)
            return dic
        else:    #这种方式获得了数据库中的个别字段  相当于select id,name from table limit = 1
            return dict(zip(model_list.keys(),model_list))

if __name__ == '__main__':
    db= SessionLocal()
    all_result  = db.query(UserItem).all()

    # list_dict = [dict(model) for model in result]

    # query_dict = query2dict(result)
    item = []
    for i in all_result:
        data = f"""{{
                
            '{i.username}':{dict(i)}
            }}"""


        item.append(data)
    print(item)
    input_name = 'admin1'
    # 根据username查询
    try:
        result = db.query(UserItem).filter(UserItem.username == input_name).one()
    except:
        result=None

    print(result)
