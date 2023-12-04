# -*- coding: utf-8 -*-
# @Time : 2023/11/30 10:48
# @Author : Z
# @Email : S
# @File : generate_token.py
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
import uvicorn


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 接口相应模型
class Token(BaseModel):
    access_token: str
    token_type: str

# app
app = FastAPI()

# 生成token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # 检测token的有效时间是否为空，如果为空，则默认设置有效时间为15分钟
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # 更新到我们之前传进来的字典
    to_encode.update({"exp": expire})
    # jwt 编码 生成我们需要的token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 请求接口
# 定义url路径，以及相应模型格式
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data通过表单数据来发送信息
#  XXX 代码占位：用户验证 XXX
    # 通常这里会先对form_data里的用户数据与数据库用户表做对比验证，验证通过则继续往下执行生成token；这里不做用户验证，直接来生成token
    # 下面设置token有效时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
# 调用token生成函数
    access_token = create_access_token(
        data={"sub": "fish"}, # 这里的data字典内容随意，可以是用户名或用户ID
        expires_delta=access_token_expires # token有效时间
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 测试使用，运行app
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
