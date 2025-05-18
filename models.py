from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Отношение один-ко-многим
    surveys = db.relationship('Survey', backref='user', lazy=True, cascade="all, delete-orphan")

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  # Название опроса
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    survey_type = db.Column(db.String(50))
    total_score = db.Column(db.Integer)  # Общий балл
    data = db.Column(db.Text)  # Все данные в JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)