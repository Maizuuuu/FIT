from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    @classmethod
    def getbyusername(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def create(cls, username, password):
        user = cls(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return user