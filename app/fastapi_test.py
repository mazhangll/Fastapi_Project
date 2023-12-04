# -*- coding: utf-8 -*-
# @Time : 2023/11/30 9:56
# @Author : Z
# @Email : S
# @File : fastapi_test.py
from fastapi import FastAPI
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse



from fastapi import FastAPI, status, HTTPException
from fastapi.responses import RedirectResponse
from app.schemas import UserOut, UserAuth
from replit import db
from app.utils import get_hashed_password
from uuid import uuid4

@app.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):
    # querying database to check if user already exist
    user = db.get(data.email, None)
    if user is not None:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    user = {
        'email': data.email,
        'password': get_hashed_password(data.password),
        'id': str(uuid4())
    }
    db[data.email] = user    # saving user to database
    return user



app = FastAPI()

@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')




@app.get('/hello')
def say_hello():
    return {'code': 200, 'message': 'hello, world!'}


if __name__ == "__main__":
    uvicorn.run(
        app='app.fastapi_test:app',
        host="0.0.0.0",
        port=8089,
        log_level="info",
        reload=True
    )