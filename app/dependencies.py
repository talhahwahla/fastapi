import jwt
from datetime import datetime, timedelta
from .config import SECRET_KEY, ALGORITHM, SQLALCHEMY_DATABASE_URL
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

# Create database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()

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

def create_access_token(data: dict, expires_delta: timedelta):
    """
    Create a JWT access token with the provided data and expiration time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
