# -*- coding: utf-8 -*-
# @Time : 2023/12/4 10:38
# @Author : Z
# @Email : S
# @File : verification_ip.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
import os
import sys
import re,socket
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curdir)

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")
    # raise "Must be using Python 3"
    #

import synonyms  # https://github.com/huyingxi/Synonyms


from fastapi import Depends, FastAPI
from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    Userans: Optional[str] = None
    Stdans: Optional[str] = None
    buzzword: Optional[str] = None



def internal(ipadd):
    '''
    判断是否为内网ip
    :param ipadd:
    :return:
    '''
    a=re.findall(r'^((192\.168)|(10\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d))|(172\.(1[6-9]|2[0-9]|3[0-1])))\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$',ipadd)
    if a:
        # print('ture')
        return True



def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    # print(ip)
    return ip

app = FastAPI()




@app.post("/compare/")
async def compare(item:Item):
    # sen1 = "一个人"
    # sen2 = "两个人"

    ip = get_host_ip()
    is_internal = internal(ip)

    if is_internal:
        sen1 = item.Userans
        sen2 = item.Stdans
        buzzword = item.buzzword
        if sen1 and sen2 and not buzzword:
            r = synonyms.compare(sen1, sen2, seg=False)
            print("%s vs %s" % (sen1, sen2), r)
            if r > 0.5:
                return {
                    "num": r,
                    "str": "相似"
                }
            else:
                return {
                    "num": r,
                    "str": "不相似"
                }
            return r
        if buzzword:
            sentence = "手机业务将遭受重创。"
            keywords = synonyms.keywords(buzzword, topK=5, withWeight=True, allowPOS=())
            keywords2 = []
            for word in keywords:
                word2 = []
                num = buzzword.count(word[0])
                word2.append(word[0])
                word2.append(word[1])
                word2.append(num)
                keywords2.append(word2)



            return {
                "keywords": keywords2
            }
        else:
            return {
                "message": '请传入正确参数'
            }


