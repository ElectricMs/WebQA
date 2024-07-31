# 创建 Pydantic 模型
#
# 为了避免 SQLAlchemy模型和 Pydantic模型之间的混淆，我们将有models.py（SQLAlchemy 模型的文件）
# 和schema.py（ Pydantic 模型的文件）。
# 这些 Pydantic 模型或多或少地定义了一个“schema”（一个有效的数据形状）。
#
# #SQLAlchemy模型：用于数据库操作，如查询、插入、更新和删除。
# 它们是数据库操作的基础，允许开发者通过Python类和对象来执行SQL操作。
# Pydantic模型：用于API的输入验证和输出格式化，确保客户端和服务器之间的数据传输是正确的。


from pydantic import BaseModel


class ChatBase(BaseModel):
    user_id: int


class ChatCreate(ChatBase):
    pass


class Chat(ChatBase):
    chat_id: int

    # Pydantic orm_mode将告诉 Pydantic模型读取数据，
    # 即它不是一个dict，而是一个 ORM 模型（或任何其他具有属性的任意对象）
    class Config:
        from_attributes = True  # 设置配置值，而不是声明类型


class UserBase(BaseModel):
    account: str
    password: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    token: str
    # 由于SQLAlchemy的relationship功能失效，在user实例中不存储chat_id，改为通过user_id在Chat表中检索
    # chats: list[Chat] = []

    class Config:
        from_attributes = True
