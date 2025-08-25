from datetime import datetime
from app import db

class Address(db.Model):
    __tablename__ = 'addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label = db.Column(db.String(50), nullable=True)  # Home, Office, etc.
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address_line1 = db.Column(db.String(200), nullable=False)
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    landmark = db.Column(db.String(200))
    is_default = db.Column(db.Boolean, default=False)
    
    # GPS coordinates for future delivery optimization
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='user_addresses', lazy=True)
    orders = db.relationship('Order', backref='delivery_address', lazy=True)
    
    @property
    def full_address(self):
        """Return complete formatted address"""
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        if self.landmark:
            address_parts.append(f"Near {self.landmark}")
        address_parts.extend([self.city, self.state, self.pincode])
        return ", ".join(address_parts)
    
    @property
    def short_address(self):
        """Return shortened address for display"""
        return f"{self.address_line1}, {self.city} - {self.pincode}"
    
    def set_as_default(self):
        """Set this address as default and unset others"""
        # First, unset all other addresses for this user
        Address.query.filter_by(user_id=self.user_id, is_default=True).update({'is_default': False})
        # Set this address as default
        self.is_default = True
        db.session.commit()
    
    def __repr__(self):
        return f'<Address {self.label}: {self.short_address}>'