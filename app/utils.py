# -*- coding: utf-8 -*-
# @Time : 2023/11/30 10:24
# @Author : Z
# @Email : S
# @File : utils.py
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 密码散列
def get_hashed_password(password: str) -> str:
	"""
	get_hashed_password 函数接收一个普通密码，并返回可以安全存储在数据库中的哈希值。
	:param password:
	:return:
	"""

	return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
	"""
	verify_password 函数接收普通密码和散列密码，并返回一个布尔值，代表密码是否匹配。
	:param password:
	:param hashed_pass:
	:return:
	"""
	return password_context.verify(password, hashed_pass)



# 生成JWT令牌
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']    # should be kept secret

# 生成访问令牌
def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
	if expires_delta is not None:
		expires_delta = datetime.utcnow() + expires_delta
	else:
		expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

	to_encode = {"exp": expires_delta, "sub": str(subject)}
	encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
	return encoded_jwt

# 刷新令牌的函数
def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
	if expires_delta is not None:
		expires_delta = datetime.utcnow() + expires_delta
	else:
		expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

	to_encode = {"exp": expires_delta, "sub": str(subject)}
	encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
	return encoded_jwt


# https://juejin.cn/post/7106787575033298952


if __name__ == '__main__':
	password = get_hashed_password('aaa')
	print(password)

