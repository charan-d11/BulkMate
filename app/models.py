from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)              # for calorie calculation
    goal = db.Column(db.String(20))           # 'gain' / 'maintain' / 'lose'
    activity_level = db.Column(db.String(20))  # 'sedentary', 'light', 'moderate', 'active', 'very active'
    goal_calories = db.Column(db.Integer)     # auto calculated on onboarding

    otp_code       = db.Column(db.String(6),  nullable=True)
    otp_expiry     = db.Column(db.DateTime,   nullable=True)
    otp_verified   = db.Column(db.Boolean,    default=False)
    
    # Relationships
    meals = db.relationship('Meal', backref='user', lazy=True)
    chats = db.relationship('ChatHistory', backref='user', lazy=True)


class Meal(db.Model):
    __tablename__ = 'meal'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    food_name = db.Column(db.String(200))
    calories = db.Column(db.Float, default=0.0)
    protein = db.Column(db.Float, default=0.0)
    carbs = db.Column(db.Float, default=0.0)
    fat = db.Column(db.Float, default=0.0)


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20))       # 'user' or 'assistant'
    message = db.Column(db.Text)