from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine
from fastapi import APIRouter, Depends


router = APIRouter()




# models.Base.metadata.create_all(bind=engine)


# Dependency
# 每个请求有一个独立的数据库会话/连接（SessionLocal），在整个请求中使用相同的会话，然后在请求完成后关闭它。
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 创建账户路由 已测试 会验证账号是否存在 后续需要验证传入的数据结构
@router.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_account(db, user_account=user.account)
    if db_user:
        raise HTTPException(status_code=400, detail="Account already registered")
    return crud.create_user(db=db, user=user)


# 登录路由 需要验证传入信息格式
@router.post("/login", response_model=schemas.User)
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.login(db=db, user=user)


# 此路由只测试用
@router.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# @router.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @router.post("/users/{user_id}/chats/", response_model=schemas.Chat)
# def create_chat_for_user(
#     user_id: int, chat: schemas.ChatCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_chat(db=db, chat=chat, chat_id=chat_id)


# @router.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items
