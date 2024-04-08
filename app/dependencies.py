import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from .config import SECRET_KEY, ALGORITHM, SQLALCHEMY_DATABASE_URL
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext
from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer

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


# Create a new instance of CryptContext for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    """
    Verify that the plain password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_id_from_token(token: str = Security(oauth2_scheme)):
    """
    Extract the user ID from the JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[int] = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_email_from_token(token: str = Security(oauth2_scheme)):
    """
    Extract the email from the JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_token(authorization: str = Security(oauth2_scheme)):
    """
    Extract the JWT token from the Authorization header.
    """
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme")
        return token
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid authorization header")
    