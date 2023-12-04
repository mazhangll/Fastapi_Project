# -*- coding: utf-8 -*-
# @Time : 2023/11/30 11:18
# @Author : Z
# @Email : S
# @File : token_tools.py
# -*- coding: UTF-8 -*-
import re
from datetime import datetime, timedelta
import jwt
from fastapi import Depends, FastAPI, HTTPException,Request
from fastapi.responses import JSONResponse,RedirectResponse
from ipaddress import ip_address
from starlette import status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from passlib.context import CryptContext  # passlib 处理哈希加密的包
from pydantic import BaseModel
from app.UserDao import get_alluser,get_db
import  time
# to get a string like this run: openssl rand -hex 32
from app import model
from app.database import SessionLocal

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # 密钥
ALGORITHM = "HS256"  # 算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 访问令牌过期分钟

'''用户数据（模拟数据库用户表）；账号：johndoe 密码：secret
   用于我们稍后验证。'''

# fake_users_db = {
#     "zhangll": {
#         "username": "zhangll",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "Zjhc123!@#",
#         "disabled": False,
#     },
# "alice": {
#         "username": "alice",
#         "full_name": "Alice Chains",
#         "email": "alicechains@example.com",
#         "hashed_password": "$2b$12$gSvqqUPvlXP2tfVFaWK1Be7DlH.PKZbv5H8KnzzVgXXbVxpva.pFm",
#         "disabled": True,
#     },
# # }
fake_users_db = get_alluser()

# $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW
'''FastAPI参数类型验证模型'''
# token url相应模型
class Token(BaseModel):
    access_token: str
    token_type: str

# 令牌数据模型
class TokenData(BaseModel):
    username: str = None

"""
这里注意字段匹配类型
"""
# 用户基础模型
class User(BaseModel):
    # username: str
    # email: str = None
    # full_name: str = None
    # disabled: bool = None
    userid :int
    loginname : str
    username : str
    # is_active = Column(Boolean, default=True)
    remark : str
    statusid: int

 # 用户输入数据模型
class UserInDB(User):
    passwd: str

'''为了数据安全，我们利用PassLib对入库的用户密码进行加密处理，推荐的加密算法是"Bcrypt"
其中，我们主要使用下面方法：
    pwd_context.hash(password) # 对密码进行加密
    pwd_context.verify(plain_password, hashed_password) 对密码进行校验
    ----- 具体使用可见后面代码 ------
'''
# Context是上下文,CryptContext是密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context)
# oauth2_scheme是令牌对象，token: str = Depends(oauth2_scheme)后就是之前加密的令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
'''
OAuth2PasswordBearer是接收URL作为参数的一个类：客户端会向该URL发送username和password参数，然后得到一个token值。
OAuth2PasswordBearer并不会创建相应的URL路径操作，只是指明了客户端用来获取token的目标URL。
当请求到来的时候，FastAPI会检查请求的Authorization头信息，如果没有找到Authorization头信息，或者头信息的内容不是Bearer token，它会返回401状态码(UNAUTHORIZED)。
'''

# 这是我们的app应用
app = FastAPI()


# verify_password验证密码
# plain_password普通密码, hashed_password哈希密码
# 返回True和False
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
    # return plain_password==hashed_password

# 获取哈希密码;普通密码进去，对应的哈希密码出来。
def get_password_hash(password):

    return pwd_context.hash(password)

# 模拟从数据库读取用户信息
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)



# 验证用户,username，password是OAuth2PasswordRequestForm输入的参数
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    verify_result = verify_password(password, user.passwd)
    if not user or not verify_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# 创建访问令牌（token），data={"sub": user.username}
def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta  # expire 令牌到期时间
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

''' ----  登录验证，获取token的接口 --------
    用户发送post请求获取token,后端验证该用户是否存在，密码是否正确。如果验证通过，会生成‘token’给到用户。'''
# name = johndoe    password = secret
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # 使用数据库查询
    fake_users_db = get_alluser()
    # 1、验证用户
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)  # 验证用户
    # 2、access_token_expires访问令牌过期时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # timedelta表示两个datetime对象之间的差异。（来自datetime包）
    # 3、create_access_token创建访问令牌
    access_token = create_access_token(data={"sub": user.loginname},expires_delta=access_token_expires)
    # 返回
    return {"access_token": access_token, "token_type": "bearer"}


########## 新货分界线 ###########

'''数据请求验证
用户拿到token信息后，必须在后续请求中，头信息的Authorization带有Bearer token，才能访问其他数据接口。
下面添加一个校验函数，对请求的合法性进行校验，读取token内容解析并进行验证，验证token通过后，获取接口响应数据'''

# 获取当前用户
# 通过oauth2_scheme，拿到用户请求头文件里的token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # jwt 解码
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 通常在jwt 解码会进行验证抛出各种异常PyJWTError，如令牌过期等；
        # 获取生成token时候，我们放进去的username信息
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    # 获取该用户信息
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# 获取当前激活用户，通过数据库信息及相关条件对用户有效性进行过滤；如该用户存在，密码正确，token验证通过，但数据库字段显示该用户被封号或欠费了（非激活用户），就这此处触发异常，结束访问。
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    # 如果用户状态不可用，抛出异常
    if not current_user.statusid:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# 判断是否为ipv4
def is_public_ipv4(ip: str) -> bool:
    try:
        return not ip_address(ip).is_private
    except ValueError:
        return False

@app.get("/")
async def root(request: Request):
    client_host = request.client.host
    if is_public_ipv4(client_host):
        return {"message": "Welcome to the API"}
    else:
        return JSONResponse(status_code=403, content={"message": "Forbidden"})



# 使用中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    request.
一个函数 call_next 它将接收 request 作为参数.
这个函数将 request 传递给相应的 路径操作.
然后它将返回由相应的路径操作生成的 response.
然后你可以在返回 response 前进一步修改它.
    :param request:
    :param call_next:
    :return:
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # 添加项响应头
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def verification_ip(request: Request, call_next):
    ip = request.client.host
    is_internal = internal(ip)
    # 不是内网
    if not is_internal:
        result = {
            "ip": request.client.host,
            "x-real-ip": request.headers.get("X-Real-Ip", ""),
            "x-forwarded-for": request.headers.get("x-forwarded-for", ""),
            "是否为内网": is_internal
        }

        response = await call_next(request)
        response.headers["X-Process-ip"] = str(ip)
        return response
    else:
        return JSONResponse(status_code=403, content={"message": "Forbidden"})

def internal(ipadd):
    '''
    判断是否为内网ip
    :param ipadd:
    :return:
    '''
    a=re.findall(r'^((192\.168)|(10\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d))|(172\.(1[6-9]|2[0-9]|3[0-1])))\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$',ipadd)
    result = True if a else False
    # if a:
    #     # print('ture')
    #     return True
    return  result


# 获取ip
@app.get("/ip")
async def root(request: Request):
    ip = request.client.host
    is_internal = internal(ip)
    result={
        "ip":request.client.host,
        "x-real-ip":request.headers.get("X-Real-Ip",""),
        "x-forwarded-for":request.headers.get("x-forwarded-for",""),
        "是否为内网":is_internal
    }
    return result


# 数据请求接口（获得自己的数据库信息），依赖上面的校验函数
@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    print("测试token")
    return current_user

@app.get("/hello")
async def say_hello(current_user: User = Depends(get_current_active_user)):
    print("测试token")
    return "hello"

# 获取全部用户
app.get("/get_alluser")(get_alluser)





# 测试使用，运行app
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
    # password_hash = get_password_hash("secret")
    # print(password_hash)
