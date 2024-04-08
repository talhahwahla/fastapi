from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from . import models, schemas
from .models import SessionLocal, engine
from . import dependencies
from .config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


@router.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    # Check if the email is already registered
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Create a new user in the database
    new_user = models.User(email=user.email, password=user.password)
    db.add(new_user)
    db.commit()

    # Generate a JWT token for the new user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = dependencies.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"token": access_token}


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(dependencies.get_db)):
    # Implement login logic here
    # Verify user credentials and return a token
    return {"token": "your_token_here"}


@router.post("/add_post", response_model=schemas.PostResponse)
def add_post(post: schemas.PostCreate, token: str = Depends(dependencies.get_token), db: Session = Depends(dependencies.get_db)):
    # Implement add_post logic here
    # Add the post to the database and return the post ID
    return {"id": 1, "text": post.text, "created_at": "2024-04-09T12:00:00Z", "author": {"id": 1, "email": "user@example.com"}}


@router.get("/get_posts", response_model=List[schemas.PostResponse])
def get_posts(token: str = Depends(dependencies.get_token), db: Session = Depends(dependencies.get_db)):
    # Implement get_posts logic here
    # Retrieve all posts for the user from the database
    return [{"id": 1, "text": "Post 1", "created_at": "2024-04-09T12:00:00Z", "author": {"id": 1, "email": "user@example.com"}}]


@router.delete("/delete_post")
def delete_post(post_id: int, token: str = Depends(dependencies.get_token), db: Session = Depends(dependencies.get_db)):
    # Implement delete_post logic here
    # Delete the post from the database
    return {"message": "Post deleted successfully"}
