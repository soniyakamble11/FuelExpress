from datetime import datetime
from app import db

class FuelStation(db.Model):
    __tablename__ = 'fuel_stations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    owner = db.relationship('User', back_populates='stations', lazy=True)
    
    fuel_types = db.relationship('FuelType', backref='station', lazy=True)

    def __repr__(self):
        return f'<FuelStation {self.name}>'
