# -*- coding: utf-8 -*-
# @Time : 2023/12/1 8:57
# @Author : Z
# @Email : S
# @File : UserDao.py
from app.database import SessionLocal
from app.model import UserItem

from fastapi import FastAPI, Depends
import hashlib
from sqlalchemy.orm import Session
from app.model import *
from decimal import Decimal, getcontext

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def get_alluser(db: Session = Depends(get_db)):
    db = SessionLocal()
    # query = "SELECT * FROM t_users"
    # db.execute(query)
    # result = db.fetchall()
    result = db.query(UserItem).all()

    # list_dict = [dict(model) for model in result]

    # query_dict = query2dict(result)
    # item = []
    # for i in result:
    #     data = f"{i.username}:{dict(i)}"
    #     item.append(data)

    # 组合成fake_users_db
    fake_users_db = {}
    for user in result:
        fake_users_db[user["loginname"]] = {
            "userid":user["userid"],
            "loginname": user["loginname"],
            "username": user["username"],
            "passwd": user["passwd"],
            "remark": user["remark"] if None else '',
            "statusid": int(user["statusid"]) ,

        }

    if fake_users_db:
        return fake_users_db
    # return {
    #     "message":"secusess",
    #     "data": result}
    else:
        return {"error": "User not found"}


def get_user(username: str, db: Session = Depends(get_db)):
    """
    根据姓名查询
    :param username:
    :param db:
    :return:
    """
    db = SessionLocal()
    # 根据username查询
    try:
        user = db.query(UserItem).filter(UserItem.username == username).one()
        user = dict(user)
        return user
    except:
        result = None
        return result



if __name__ == '__main__':

    alluser = get_alluser()
    print(alluser)