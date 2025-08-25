from app import db
from app.models.user import User

# Importing new customer dashboard models
from app.models.fuel import FuelType
from app.models.address import Address
from app.models.order import Order, OrderTracking, OrderStatus

__all__ = [
    'db',
    'User',
    'FuelType',
    'Address', 
    'Order',
    'OrderTracking',
    'OrderStatus'
]