import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 数据库连接配置（请根据实际环境修改连接参数）
DATABASE_URL = "mysql+pymysql://root:mysql123@localhost:3306/ac_db"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True, future=True)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

# 创建基础模型类
Base = declarative_base()

# 获取数据库会话（生成器方式使用，可在FastAPI等框架中调用）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
