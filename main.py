from datetime import datetime

from passlib.hash import bcrypt

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from db import Post, get_db, User
from models import PostBase, PostCreate, SignInModel, SignUpModel, UserModel


app = FastAPI()


templates = Jinja2Templates('templates')


# TEMPLATES  

@app.get('/')
def index(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return templates.TemplateResponse('index.html', {'request': request, 'posts': posts})


@app.get('/{post_id}/', response_model=PostBase)
def post_detail(post_id:int, request:Request, db: Session=Depends(get_db)):
    post = db.query(Post).filter(Post.id==post_id).first()
    if post:
        return templates.TemplateResponse('detail.html', {'post': post, 'request': request})
    else:
        return templates.TemplateResponse('404.html', {'request': request})


@app.get('/create')
def home(request: Request):
    return templates.TemplateResponse('create.html', {'request': request})


@app.post('/post-created/')
def post_created(post: PostCreate, request: Request, db: Session=Depends(get_db)):
    post_data = Post(**post.dict())
    db.add(post_data)
    db.commit()
    db.refresh(post_data)
    return RedirectResponse('/')


@app.post('/delete/{post_id}')
def delete_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id==post_id).first()
    if post:
        db.delete(post)
        db.commit()
        return RedirectResponse('/', method='GET')
    return templates.TemplateResponse('404.html', status_code=404)


# API

# User
@app.post('/api/v1/sign-up/')
def sign_up_api(data: SignUpModel, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email==data.email).first():
        raise HTTPException(status_code=404, detail='Email is already taken')
    if data.password != data.password_confirm:
        raise HTTPException(status_code=400, detail='Password is not matching')
    user = User(email=data.email,
                hashed_password=bcrypt.hash(data.password), 
                first_name='', 
                last_name='')
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get('/api/v1/user-list/', response_model=list[UserModel])
def user_list_api(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users



@app.get('/api/v1/user/detail/{user_id}')
def get_user_api(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id==user_id).options(joinedload(User.posts)).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail='User not found')



@app.put('/api/v1/user/update/{user_id}')
def update_user_api(user_data: UserModel, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id==user_data.id).first()
    if user:
        user.first_name = user_data.first_name
        user.last_name = user_data.last_name
        user.email = user_data.email
        user.updated_at = datetime.now()
        db.commit()
        db.refresh(user)
        return user
    raise HTTPException(status_code=404, detail='User not found')


# Post
@app.post('/api/v1/post/create/', response_model=PostBase)
def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    post = Post(**post_data.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@app.get('/api/v1/post/list/', response_model=list[PostBase])
def list_post_api(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts


@app.get('/api/v1/post/detail/{post_id}', response_model=PostBase)
def detail_post_api(post_id: int, db: Session=Depends(get_db)):
    post = db.query(Post).filter(Post.id==post_id).first()
    return post



@app.delete('/api/v1/post/delete/{post_id}')
def delete_post_api(post_id: int, db: Session = Depends (get_db)):
    post = db.query(Post).filter(Post.id==post_id).first()
    if post:
        db.delete(post)
        db.commit()
        return JSONResponse(status_code=200, content={'message': 'Post successfully deleted'})
    else:
        raise HTTPException(status_code=404, detail='Post not found')
    

@app.put('/api/v1/post/update/{post_id}')
def update_post_api(post_id: int, post_data: PostCreate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id==post_id).first()
    if post:
        post.title = post_data.title
        post.text = post_data.text
        post.updated_at = datetime.now()
        db.commit()
        db.refresh(post)
        return post
    raise HTTPException(status_code=404, detail='Post not found')


@app.patch('/api/v1/post/partial-update/{post_id}')
def partial_update_post_api(post_id: int, post_data: PostCreate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id==post_id).first()
    if post:
        if post_data.title:
            post.title = post_data.title
        if post_data.text:
            post.text = post_data.text

        post.updated_at = datetime.now()
        db.commit()
        db.refresh(post)
        return post
    raise HTTPException(status_code=404, detail='Post not found')


@app.get('/api/v1/post/user-posts/{user_id}')
def user_posts_api(user_id: int, db: Session = Depends(get_db)):
    user_posts = db.query(Post).filter(Post.user_id==user_id)
    if user_posts:
        return user_posts
    raise HTTPException(404, 'No posts found')