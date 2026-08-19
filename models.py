from datetime import datetime
from database import db

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(100), unique=True, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    style = db.Column(db.String(50), nullable=False, default='cinematic')
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(500))

    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'prompt': self.prompt,
            'style': self.style,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'url': self.url
        }
