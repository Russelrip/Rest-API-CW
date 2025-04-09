from datetime import datetime
from app.database import db
from sqlalchemy.orm import relationship

class APIUsage(db.Model):
    """Model for tracking API usage"""
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status_code = db.Column(db.Integer, nullable=False)
    response_time_ms = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Relationships
    api_key = relationship('APIKey', back_populates='usage_logs')
    
    def __init__(self, api_key_id, endpoint, method, status_code, 
                response_time_ms=None, ip_address=None, user_agent=None):
        """Initialize a new API usage log"""
        self.api_key_id = api_key_id
        self.endpoint = endpoint
        self.method = method
        self.status_code = status_code
        self.response_time_ms = response_time_ms
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def to_dict(self):
        """Convert usage log to dictionary"""
        return {
            'id': self.id,
            'api_key_id': self.api_key_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'timestamp': self.timestamp.isoformat(),
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
    
    def __repr__(self):
        return f"<APIUsage {self.id} - Key {self.api_key_id} - Endpoint {self.endpoint}>"