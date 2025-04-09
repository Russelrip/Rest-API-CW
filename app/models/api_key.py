import uuid
from datetime import datetime, timedelta
from app.database import db, bcrypt
from sqlalchemy.orm import relationship

class APIKey(db.Model):
    """Model for storing API keys"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key_value = db.Column(db.String(255), unique=True, nullable=False)
    key_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    last_used = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='api_keys')
    usage_logs = relationship('APIUsage', back_populates='api_key', cascade='all, delete-orphan')
    
    def __init__(self, user_id, name=None, expires_in_days=365):
        """Initialize a new API key"""
        self.user_id = user_id
        self.name = name
        # Generate a unique API key using UUID
        self.key_value = str(uuid.uuid4())
        # Store a hash of the key for verification
        self.key_hash = bcrypt.generate_password_hash(self.key_value).decode('utf-8')
        # Set expiration date
        if expires_in_days:
            self.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    def check_key(self, key):
        """Verify if provided key matches stored hash"""
        return bcrypt.check_password_hash(self.key_hash, key)
    
    def is_valid(self):
        """Check if key is active and not expired"""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def log_usage(self):
        """Update last used timestamp"""
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def revoke(self):
        """Disable the API key"""
        self.is_active = False
        db.session.commit()
    
    def extend(self, days=365):
        """Extend key expiration"""
        if self.expires_at:
            self.expires_at = self.expires_at + timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
    
    def to_dict(self):
        """Convert API key object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key_value,  # Only returned when first created
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }
    
    def to_safe_dict(self):
        """Convert API key object to dictionary without revealing key value"""
        data = self.to_dict()
        # Remove the actual key
        del data['key']
        return data
    
    def __repr__(self):
        return f"<APIKey {self.id} - User {self.user_id}>"