from typing import Optional

from fastapi import HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine
from fastapi import APIRouter, Depends

router = APIRouter()


models.Base.metadata.create_all(bind=engine)


# Dependency
# 每个请求有一个独立的数据库会话/连接（SessionLocal），在整个请求中使用相同的会话，然后在请求完成后关闭它。
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ADMIN_TOKEN_PATH = "/_token"


class TokenVerificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(ADMIN_TOKEN_PATH):
            token = request.headers.get("token")
            try:
                # 在这里调用verify_token函数
                # 注意：不能直接在中间件中使用Depends，因此需要手动获取db会话
                db = next(get_db())
                verify_token(token=token, db=db)
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"code": e.status_code, "msg": e.detail}
                )

        response = await call_next(request)
        return response


def verify_token(token: Optional[str] = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=403, detail="请先登录")

    admin_token_sql = text("SELECT * FROM `User` WHERE `token` = :token")
    result = db.execute(admin_token_sql, {'token': token})
    admin = result.fetchone()

    if not admin:
        raise HTTPException(status_code=403, detail="请先登录")

    return admin


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


# 获取历史记录id的路由 需登录 请求头中传递user_id
# 后续验证user_id和token是否一致
# 返回一个列表，每个元素内包含chat_id和user_id
# 若找不到任何历史记录 则会返回空列表
@router.get("/_token/history", response_model=list[schemas.Chat])
def get_user_chats(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_chats(db, user_id=user_id)
    # if db_user is None:
    #     raise HTTPException(status_code=404, detail="CHat not found")
    return db_user


# 创建新的对话 添加历史记录id
@router.post("/_token/create", response_model=schemas.Chat)
def create_chat_for_user(
    chat: schemas.ChatCreate, db: Session = Depends(get_db)
):
    return crud.create_user_chat(db=db, chat=chat)
