from fastapi import Depends
from sqlalchemy.orm import Session


from main import app
from models import PostCreate
from db import Post, get_db

@app.post('/api/v1/create/', response_model=PostCreate)
def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    post = Post(**post_data.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post