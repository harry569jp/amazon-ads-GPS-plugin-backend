# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL # 从 config.py 导入

if not DATABASE_URL:
    raise ValueError("请通过环境变量 DATABASE_URL 设置数据库连接字符串")

# 检查URL是否为Supabase，如果是，则添加SSL要求
connect_args = {}
if "supabase" in DATABASE_URL:
    connect_args = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()