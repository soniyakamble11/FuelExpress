from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('customer', 'delivery_partner', 'station_owner', 'admin'),
        default='customer',
        nullable=False
    )
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # NEW: link station_owner to FuelStation
    stations = db.relationship('FuelStation', back_populates='owner', lazy=True)

    @property
    def name(self):
        return str(self.username) if self.username else ""

    @name.setter
    def name(self, value):
        self.username = value

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_customer(self): 
        return self.role == 'customer'
    
    def is_station_owner(self): 
        return self.role == 'station_owner'
    
    def is_delivery_partner(self): 
        return self.role == 'delivery_partner'
    
    def is_admin(self): 
        return self.role == 'admin'

    # DASHBOARD & ORDERS METHODS
    def get_default_address(self):
        from app.models.address import Address
        return Address.query.filter_by(user_id=self.id, is_default=True).first()

    def get_recent_orders(self, limit=5):
        from app.models.order import Order
        return Order.query.filter_by(customer_id=self.id).order_by(Order.created_at.desc()).limit(limit).all()

    def get_total_orders_count(self):
        from app.models.order import Order
        return Order.query.filter_by(customer_id=self.id).count()

    def get_total_fuel_ordered(self):
        from app.models.order import Order
        from sqlalchemy import func
        result = db.session.query(func.sum(Order.quantity_liters)).filter_by(customer_id=self.id).scalar()
        return result or 0.0

    def get_addresses(self):
        from app.models.address import Address
        return Address.query.filter_by(user_id=self.id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()

    def get_total_spent(self):
        from app.models.order import Order
        from sqlalchemy import func
        result = db.session.query(func.sum(Order.total_amount)).filter_by(customer_id=self.id).scalar()
        return result or 0.0

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
