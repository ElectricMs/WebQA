# 创建 SQLAlchemy 部件
# https://fastapi.tiangolo.com/zh/tutorial/sql-databases/
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy import event


# 定义事件监听器
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app/SQLite.sqlite3"
# 如果使用的是PostgreSQL数据库
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(  # 创建 SQLAlchemy 引擎
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# 每个SessionLocal类的 实例 都会是一个数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 将继承这个类，来创建每个数据库模型或类（ORM 模型）
Base = declarative_base()
