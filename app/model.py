# -*- coding: utf-8 -*-
# @Time : 2023/11/30 18:39
# @Author : Z
# @Email : S
# @File : model.py
# models.py

from sqlalchemy import Column, String, Integer

from database import Base, engine


class UserItem(Base):
	__tablename__ = 'model_authorize_manage'  # 数据库表名
	manage_id  = Column(Integer, primary_key=True, index=True)
	accesskey = Column(String)
	customer = Column(String)
	secretkey = Column(String)
	# is_active = Column(Boolean, default=True)
	remark = Column(String)
	status = Column(Integer)

	def keys(self):
		return ["manage_id","accesskey", "customer","secretkey","remark" ,"status"]

	def __getitem__(self, item):
		return self.__getattribute__(item)

if __name__ == '__main__':
	Base.metadata.create_all(engine)
