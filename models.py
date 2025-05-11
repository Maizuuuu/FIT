from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()



class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    survey_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    result_data = db.Column(db.Text)

    def __repr__(self):
        return f'<Survey {self.id}>'
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    workouts = db.relationship('Workout', backref='user', lazy=True)

    # Добавляем метод для поиска по username
    @classmethod
    def getbyusername(cls, username):
        return cls.query.filter_by(username=username).first()

    def __repr__(self):
        return f'<User {self.username}>'

class Workout(db.Model):
    __tablename__ = 'workouts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    plan = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Workout {self.goal} {self.created_at}>'