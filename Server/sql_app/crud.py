import uuid

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
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
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_account(db: Session, user_account: str):
    return db.query(models.User).filter(models.User.account == user_account).first()


def login(db: Session, user: schemas.UserCreate):
    result = db.query(models.User).filter(models.User.account == user.account,
                                          models.User.password == user.password).first()
    if result:
        result.token = str(uuid.uuid4())
        # 如在此处更新token
        db.query(models.User).filter(models.User.account == user.account, models.User.password == user.password).update(
            {'token': result.token})
        result.password = ""
        return result
    raise HTTPException(status_code=400, detail="Account or password is incorrect")


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    # 考虑对密码进行哈希加密
    # fake_hashed_password = user.password + "notreallyhashed"
    user_id = new_id()
    db_user = models.User(account=user.account, password=user.password, id=user_id, token=str(uuid.uuid4()))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_user.password = ""
    return db_user


def get_chats(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Chat).offset(skip).limit(limit).all()


def create_user_chat(db: Session, chat: schemas.ChatCreate, chat_id: int):
    # chat_id = new_id()  # 后面改成自增形式？
    db_chat = models.Chat(**chat.dict(), chat_id=chat_id)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat
