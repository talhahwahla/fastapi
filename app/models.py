from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel
from datetime import datetime

Base = declarative_base()


# SQLAlchemy models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    posts = relationship("Post", back_populates="author")


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey('users.id'))

    author = relationship("User", back_populates="posts")


# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    text: str


class PostResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
    author: UserResponse

    class Config:
        orm_mode = True


# Create database engine
SQLALCHEMY_DATABASE_URL = "mysql://user:password@localhost/db_name"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
