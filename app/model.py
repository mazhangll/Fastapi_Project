# -*- coding: utf-8 -*-
# @Time : 2023/11/30 18:39
# @Author : Z
# @Email : S
# @File : model.py
# models.py

from sqlalchemy import Column, String, Integer

from database import Base, engine


class UserItem(Base):
	__tablename__ = 'biz_user_sysuser'  # 数据库表名
	userid = Column(Integer, primary_key=True, index=True)
	loginname = Column(String)
	username = Column(String)
	passwd = Column(String)
	# is_active = Column(Boolean, default=True)
	remark = Column(String)
	statusid = Column(Integer)

	def keys(self):
		return ["userid","loginname", "username","passwd","remark" ,"statusid"]

	def __getitem__(self, item):
		return self.__getattribute__(item)

if __name__ == '__main__':
	Base.metadata.create_all(engine)
