from datetime import datetime
from enum import Enum
import random
import string
from app import db


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Customer Info
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Fuel Details
    fuel_type_id = db.Column(db.Integer, db.ForeignKey('fuel_types.id'), nullable=False)
    fuel_type = db.relationship("FuelType", back_populates="orders", lazy=True) 
    quantity_liters = db.Column(db.Float, nullable=False)
    price_per_liter = db.Column(db.Float, nullable=False)  # Price at time of order
    total_fuel_cost = db.Column(db.Float, nullable=False)
    
    # Delivery Details
    delivery_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    delivery_time_slot = db.Column(db.String(20), nullable=False)  # e.g., "09:00-11:00"
    delivery_fee = db.Column(db.Float, default=0.0)
    
    # Pricing
    total_amount = db.Column(db.Float, nullable=False)  # fuel_cost + delivery_fee
    
    # Order Status
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    status_updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Special Instructions
    special_instructions = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='orders', lazy=True, foreign_keys=[user_id])
    tracking_history = db.relationship('OrderTracking', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    def generate_order_number(self):
        """Generate unique order number: FE240822001"""
        date_str = datetime.utcnow().strftime('%y%m%d')
        random_suffix = ''.join(random.choices(string.digits, k=3))
        return f"FE{date_str}{random_suffix}"
    
    @property
    def status_display(self):
        """Human readable status"""
        status_map = {
            OrderStatus.PENDING: "Order Placed",
            OrderStatus.CONFIRMED: "Order Confirmed", 
            OrderStatus.PREPARING: "Preparing Delivery",
            OrderStatus.OUT_FOR_DELIVERY: "Out for Delivery",
            OrderStatus.DELIVERED: "Delivered",
            OrderStatus.CANCELLED: "Cancelled"
        }
        return status_map.get(self.status, "Unknown")
    
    @property
    def status_color(self):
        """Get status color for UI"""
        color_map = {
            OrderStatus.PENDING: "warning",
            OrderStatus.CONFIRMED: "info",
            OrderStatus.PREPARING: "primary",
            OrderStatus.OUT_FOR_DELIVERY: "success",
            OrderStatus.DELIVERED: "success",
            OrderStatus.CANCELLED: "danger"
        }
        return color_map.get(self.status, "secondary")
    
    @property
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    @property
    def formatted_total(self):
        """Return formatted total amount"""
        return f"₹{self.total_amount:.2f}"
    
    @property
    def delivery_date_formatted(self):
        """Return formatted delivery date"""
        return self.delivery_date.strftime('%d %b %Y')
    
    def update_status(self, new_status, message=None):
        """Update order status and create tracking entry"""
        old_status = self.status
        self.status = new_status
        self.status_updated_at = datetime.utcnow()
        
        # Set specific timestamps
        if new_status == OrderStatus.CONFIRMED:
            self.confirmed_at = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED:
            self.delivered_at = datetime.utcnow()
        
        # Create tracking entry
        tracking = OrderTracking(
            order_id=self.id,
            status=new_status,
            message=message or f"Order status changed from {old_status.value} to {new_status.value}"
        )
        db.session.add(tracking)
        db.session.commit()
    
    def __repr__(self):
        return f'<Order {self.order_number} - {self.status.value}>'


class OrderTracking(db.Model):
    __tablename__ = 'order_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.Enum(OrderStatus), nullable=False)
    message = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def formatted_time(self):
        """Return formatted timestamp"""
        return self.created_at.strftime('%d %b %Y, %I:%M %p')
    
    def __repr__(self):
        return f'<OrderTracking {self.order_id}: {self.status.value}>'
