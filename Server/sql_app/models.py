# 创建数据库模型
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, BigInteger, VARCHAR
from sqlalchemy.orm import relationship  # 表示该表与其他相关的表中的值

from sql_app.database import Base


class User(Base):
    __tablename__ = "User"

    id = Column(BigInteger, primary_key=True)
    account = Column(VARCHAR(50), unique=True, index=True)
    password = Column(VARCHAR(50))
    token = Column(VARCHAR(50))
    # 一个ItemSQLAlchemy 模型列表（来自Chat表），这些模型具有指向User表中此记录的外键
    chat = relationship("Chat", back_populates="owner")


class Chat(Base):
    __tablename__ = "Chat"

    chat_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    # 包含表中的UserSQLAlchemy 模型User。使用user_id属性/列及其外键来了解要从User表中获取哪条记录
    owner = relationship("User", back_populates="chat")
