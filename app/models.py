from . import db
from datetime import datetime

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    phase = db.Column(db.String(50))
    tool_used = db.Column(db.String(100))
    input_data = db.Column(db.Text)
    output_data = db.Column(db.Text)
    approved_by_user = db.Column(db.Boolean, default=False)


class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)