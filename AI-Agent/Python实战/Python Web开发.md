---
title: Python Web开发
aliases:
  - Python Web开发
  - Web Development
tags:
  - python
  - web
  - flask
  - fastapi
  - django
  - rest-api
  - backend
type: wiki
status: published
created: 2026-06-28
updated: 2026-06-28
source: ""
difficulty: advanced
project: AI-Agent
---

# Python Web开发

Python拥有多个成熟的Web框架，从轻量级的Flask到全功能的Django，以及现代化的FastAPI。本页面涵盖这些框架的实战应用。

## 1. Flask框架

### 1.1 Flask基础应用

```python
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
CORS(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# 数据模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'author': self.author.username
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    posts = db.relationship('Post', backref='category', lazy=True)

# 用户加载回调
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由：首页
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    return render_template('index.html', posts=posts)

# 路由：用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已注册'}), 400
        
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

# 路由：用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            login_user(user)
            return redirect(url_for('index'))
        
        return jsonify({'error': '用户名或密码错误'}), 401
    
    return render_template('login.html')

# 路由：用户登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# 路由：创建文章
@app.route('/posts', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    
    post = Post(
        title=data['title'],
        content=data['content'],
        author=current_user,
        category_id=data.get('category_id')
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post.to_dict()), 201

# 路由：获取文章列表
@app.route('/api/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category_id = request.args.get('category_id', type=int)
    
    query = Post.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'posts': [post.to_dict() for post in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

# 路由：获取单篇文章
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())

# 路由：更新文章
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        return jsonify({'error': '无权修改'}), 403
    
    data = request.get_json()
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    
    db.session.commit()
    return jsonify(post.to_dict())

# 路由：删除文章
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        return jsonify({'error': '无权删除'}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': '文章已删除'})

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# 启动应用
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 1.2 Flask蓝图与模块化

```python
# blueprints/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from . import routes

# blueprints/auth/routes.py
from flask import request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from models import User, db

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': '登录成功', 'user': user.to_dict()})
    
    return jsonify({'error': '邮箱或密码错误'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': '已登出'})

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify(current_user.to_dict())

# blueprints/api/__init__.py
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from . import posts, users, categories

# blueprints/api/posts.py
from flask import request, jsonify
from flask_login import login_required, current_user
from . import api_bp
from models import Post, db

@api_bp.route('/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'posts': [post.to_dict() for post in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages
    })

@api_bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    
    post = Post(
        title=data['title'],
        content=data['content'],
        author_id=current_user.id,
        category_id=data.get('category_id')
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post.to_dict()), 201

# app.py - 主应用
from flask import Flask
from blueprints.auth import auth_bp
from blueprints.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

## 2. FastAPI框架

### 2.1 FastAPI基础应用

```python
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库模型
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class PostDB(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"))

# Pydantic模型
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    author: UserResponse
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 安全配置
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 创建应用
app = FastAPI(
    title="Blog API",
    description="A simple blog API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserDB).filter(UserDB.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# 路由
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 检查邮箱是否已存在
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 创建用户
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return current_user

@app.post("/posts", response_model=PostResponse)
def create_post(post: PostCreate, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db_post = PostDB(
        title=post.title,
        content=post.content,
        author_id=current_user.id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return db_post

@app.get("/posts", response_model=List[PostResponse])
def read_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    posts = db.query(PostDB).order_by(PostDB.created_at.desc()).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post: PostCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    db_post.title = post.title
    db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(db_post)
    db.commit()
    
    return {"message": "Post deleted successfully"}

# 启动事件
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2.2 FastAPI高级特性

```python
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, WebSocket
from fastapi.responses import StreamingResponse, FileResponse
import asyncio
import csv
import io
from typing import AsyncGenerator

app = FastAPI()

# 后台任务
def send_email(email: str, message: str):
    """发送邮件的后台任务"""
    import time
    time.sleep(5)  # 模拟耗时操作
    print(f"Email sent to {email}: {message}")

@app.post("/send-notification/")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Notification will be sent"}

# 文件上传
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

# 流式响应
async def generate_data() -> AsyncGenerator[str, None]:
    for i in range(10):
        yield f"data: {i}\n\n"
        await asyncio.sleep(1)

@app.get("/stream")
async def stream():
    return StreamingResponse(generate_data(), media_type="text/event-stream")

# CSV导出
@app.get("/export/csv")
async def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Email"])
    writer.writerow([1, "John", "john@example.com"])
    writer.writerow([2, "Jane", "jane@example.com"])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"}
    )

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")

# 依赖注入示例
from fastapi import Depends, Query
from typing import Optional

class CommonQueryParams:
    def __init__(
        self,
        q: Optional[str] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
    ):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends()):
    return {
        "q": commons.q,
        "skip": commons.skip,
        "limit": commons.limit
    }
```

## 3. Django框架

### 3.1 Django项目结构

```python
# settings.py - 配置文件
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key')

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方应用
    'rest_framework',
    'corsheaders',
    'django_filters',
    
    # 本地应用
    'blog.apps.BlogConfig',
    'accounts.apps.AccountsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# CORS配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# models.py - 数据模型
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    website = models.URLField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'tags'
    
    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    featured_image = models.ImageField(upload_to='posts/', null=True, blank=True)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def publish(self):
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

# serializers.py - 序列化器
from rest_framework import serializers
from .models import User, Post, Category, Tag, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'website', 'date_joined']
        read_only_fields = ['date_joined']

class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'posts_count']
    
    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'parent', 'replies', 'created_at']
        read_only_fields = ['created_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image',
            'author', 'category', 'tags', 'status', 'is_featured',
            'created_at', 'updated_at', 'published_at', 'views_count',
            'comments_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'views_count']
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

class PostCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'excerpt', 'featured_image', 'category', 'tags', 'status']

# views.py - 视图
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Category, Tag, Comment
from .serializers import PostSerializer, PostCreateSerializer, CategorySerializer, TagSerializer, CommentSerializer

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'author__username', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'views_count']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, slug=None):
        post = self.get_object()
        comments = post.comments.filter(parent=None, is_approved=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, slug=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_posts = Post.objects.filter(is_featured=True, status='published')
        serializer = PostSerializer(featured_posts, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAdminUser]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAdminUser]

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## 4. REST API设计最佳实践

### 4.1 API版本控制

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
    path('api/v2/', include('api.v2.urls')),
]

# FastAPI版本
from fastapi import FastAPI

app = FastAPI()

v1_app = FastAPI()
v2_app = FastAPI()

@v1_app.get("/posts")
def get_posts_v1():
    return {"version": "v1", "posts": []}

@v2_app.get("/posts")
def get_posts_v2():
    return {"version": "v2", "posts": [], "pagination": {}}

app.mount("/api/v1", v1_app)
app.mount("/api/v2", v2_app)
```

### 4.2 统一响应格式

```python
from typing import Any, Optional
from pydantic import BaseModel

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[list] = None
    meta: Optional[dict] = None

class PaginatedResponse(APIResponse):
    pagination: dict

# FastAPI示例
from fastapi.responses import JSONResponse

def success_response(data=None, message="Success", status_code=200):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data
        }
    )

def error_response(message="Error", errors=None, status_code=400):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "errors": errors or []
        }
    )
```

### 4.3 限流与缓存

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from functools import wraps
import time
from collections import defaultdict

app = FastAPI()

# 简单限流器
class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        minute_ago = now - 60
        
        # 清理旧请求
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        if len(self.requests[client_ip]) < self.requests_per_minute:
            self.requests[client_ip].append(now)
            return True
        return False

rate_limiter = RateLimiter(requests_per_minute=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )
    
    response = await call_next(request)
    return response

# Redis缓存
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(expire_time=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@app.get("/posts")
@cache_response(expire_time=60)
async def get_posts():
    # 数据库查询
    posts = []  # 查询数据库
    return posts
```

## 5. 部署与运维

### 5.1 Docker部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web

volumes:
  postgres_data:
```

### 5.2 Nginx配置

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server web:8000;
    }

    server {
        listen 80;
        server_name example.com;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /app/static/;
        }

        location /media/ {
            alias /app/media/;
        }
    }
}
```

## 最佳实践

### 1. 项目结构
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── schemas/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   └── utils/
├── tests/
├── alembic/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### 2. 安全实践
- 使用HTTPS
- 实施CORS策略
- 输入验证与清理
- SQL注入防护
- XSS防护
- CSRF保护

### 3. 性能优化
- 数据库查询优化
- 缓存策略
- 异步处理
- 连接池管理

### 4. 测试策略
- 单元测试
- 集成测试
- API测试
- 性能测试

## 相关页面

- [[Python自动化办公]] - 办公自动化
- [[Python爬虫实战]] - 网络爬虫
- [[Python数据处理]] - 数据处理
- [[Python机器学习实战]] - 机器学习

## 参考资源

- [Flask官方文档](https://flask.palletsprojects.com/)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Django官方文档](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

*最后更新：2026年6月28日*