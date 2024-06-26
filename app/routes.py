from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from . import models
from . import dependencies
from .config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


@router.post("/signup", response_model=models.Token)
def signup(user: models.UserCreate, db: Session = Depends(dependencies.get_db)):
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


@router.post("/login", response_model=models.Token)
def login(user: models.UserLogin, db: Session = Depends(dependencies.get_db)):
    # Check if the user with the provided email exists
    user_db = db.query(models.User).filter(models.User.email == user.email).first()
    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    # Check if the password is correct
    if not dependencies.verify_password(user.password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    # Generate a JWT token for the user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = dependencies.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {"token": access_token}

@router.post("/add_post", response_model=models.PostResponse)
def add_post(post: models.PostCreate, token: str = Depends(dependencies.get_token), db: Session = Depends(dependencies.get_db)):
    # Get the user ID from the token
    user_id = dependencies.get_user_id_from_token(token)

    # Create a new post in the database
    new_post = models.Post(text=post.text, created_at=datetime.utcnow(), author_id=user_id)
    db.add(new_post)
    db.commit()

    # Return the created post
    return {
        "id": new_post.id,
        "text": new_post.text,
        "created_at": new_post.created_at,
        "author": {
            "id": user_id,
            "email": dependencies.get_email_from_token(token)
        }
    }

@router.get("/get_posts", response_model=List[models.PostResponse])
def get_posts(token: str = Depends(dependencies.get_token), db: Session = Depends(dependencies.get_db)):
    # Get the user ID from the token
    user_id = dependencies.get_user_id_from_token(token)

    # Retrieve all posts for the user from the database
    posts = db.query(models.Post).filter(models.Post.author_id == user_id).all()

    # Return the posts
    return [{
        "id": post.id,
        "text": post.text,
        "created_at": post.created_at,
        "author": {
            "id": post.author_id,
            "email": dependencies.get_email_from_token(token)
        }
    } for post in posts]

@router.delete("/delete_post")
def delete_post(post_id: int, token: str = Depends(dependencies.get_token), db: Session = Depends(dependencies.get_db)):
    # Get the user ID from the token
    user_id = dependencies.get_user_id_from_token(token)

    # Check if the post exists and belongs to the user
    post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.author_id == user_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Delete the post from the database
    db.delete(post)
    db.commit()

    return {"message": "Post deleted successfully"}