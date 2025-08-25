from datetime import datetime
from app import db

class FuelType(db.Model):
    __tablename__ = 'fuel_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # Petrol, Diesel, CNG
    price_per_liter = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)  # Optional description
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    station_id = db.Column(db.Integer, db.ForeignKey('fuel_stations.id'))

    # Relationships
    orders = db.relationship('Order', back_populates='fuel_type', lazy=True)
    
    @property
    def formatted_price(self):
        """Return formatted price with currency symbol"""
        return f"₹{self.price_per_liter:.2f}"
    
    @classmethod
    def get_available_fuels(cls):
        """Get all available fuel types"""
        return cls.query.filter_by(is_available=True).all()
    
    def __repr__(self):
        return f'<FuelType {self.name} - {self.formatted_price}/L>'