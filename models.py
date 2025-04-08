from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return f'<User {self.username}>'

class Transcript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    call_date = db.Column(db.DateTime, nullable=False)
    quarter = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    raw_text = db.Column(db.Text)
    summary = db.Column(db.Text)
    sentiment_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transcript {self.company_name} {self.quarter} {self.year}>'

class Forecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.String(10), nullable=False)
    forecast_date = db.Column(db.DateTime, nullable=False)
    metric = db.Column(db.String(50), nullable=False)
    prediction = db.Column(db.Float, nullable=False)
    confidence_interval_low = db.Column(db.Float)
    confidence_interval_high = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Forecast {self.company_id} {self.metric} {self.forecast_date}>'   