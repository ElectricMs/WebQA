import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from source import options, generator
from sql_app import models, schemas


def new_id():
    # 生成id generator
    option = options.IdGeneratorOptions(worker_id=23, seq_bit_length=10)
    option.base_time = 12311111112
    idgen = generator.DefaultIdGenerator()
    idgen.set_id_generator(option)

    uid = idgen.next_id()
    return uid


# 编写可重用的函数用来与数据库中的数据进行交互

# #
# def get_user(db: Session, user_id: int):
#     user = db.query(models.User).filter(models.User.id == user_id).options(joinedload(models.User.chat)).first()
#     if user:
#         user.password = ""
#         return user
#     return None


# 查找账号是否已经存在 创建新账号时会使用
def get_user_by_account(db: Session, user_account: str):
    return db.query(models.User).filter(models.User.account == user_account).first()


# 登录用 登录成功后将密码清空并返回所有信息
def login(db: Session, user: schemas.UserCreate):
    result = db.query(models.User).filter(models.User.account == user.account,
                                          models.User.password == user.password).first()
    if result:
        result.token = str(uuid.uuid4())
        # 如在此处更新token
        db.query(models.User).filter(models.User.account == user.account, models.User.password == user.password).update(
            {'token': result.token})
        result.password = ""
        return {"id": result.id,
                "account": result.account,
                "password": result.password,
                "token": result.token,
                }
    raise HTTPException(status_code=400, detail="Account or password is incorrect")


# 创建新账户用 向数据库中插入信息
def create_user(db: Session, user: schemas.UserCreate):
    # 考虑对密码进行哈希加密
    # fake_hashed_password = user.password + "notreallyhashed"
    user_id = new_id()
    db_user = models.User(account=user.account, password=user.password, id=user_id, token=str(uuid.uuid4()))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_user.password = ""

    return {"id": db_user.id,
            "account": db_user.account,
            "password": db_user.password,
            "token": db_user.token,
            }


# 查找一个user_id 对应的所有聊天记录chat_id
def get_chats(db: Session, user_id: int):
    return db.query(models.Chat).filter(models.Chat.user_id == user_id).all()


# 创建新对话用 会要求user_id外键依赖于User.id 若不满足依赖则提示错误
def create_user_chat(db: Session, chat: schemas.ChatCreate):
    try:
        db_chat = models.Chat(**chat.dict())
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User ID not exists")
