from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.fuel import FuelType
from app.models.fuel_station import FuelStation
from app.models.order import Order, OrderStatus
from app import db

bp = Blueprint('owner', __name__, url_prefix='/owner')

# Dashboard
@bp.route('/dashboard')
@login_required
def dashboard():
    # Get all station IDs for this owner
    station_ids = [station.id for station in current_user.stations]

    # Fetch all fuel types for all stations of this owner
    fuels = FuelType.query.filter(FuelType.station_id.in_(station_ids)).all()

    # Fetch all orders for these stations
    orders = Order.query.join(FuelType).filter(FuelType.station_id.in_(station_ids)).all()

    return render_template('owner/dashboard.html', fuels=fuels, orders=orders)

# Orders Page
@bp.route('/orders')
@login_required
def orders():
    station_ids = [station.id for station in current_user.stations]
    orders = Order.query.join(FuelType).filter(FuelType.station_id.in_(station_ids)).all()
    return render_template('owner/orders.html', orders=orders)

# Update Fuel
@bp.route('/fuel/update/<int:fuel_id>', methods=['GET','POST'])
@login_required
def update_fuel(fuel_id):
    fuel = FuelType.query.get_or_404(fuel_id)
    if request.method == 'POST':
        fuel.price_per_liter = float(request.form['price'])
        fuel.is_available = True if 'available' in request.form else False
        db.session.commit()
        flash('Fuel updated successfully', 'success')
        return redirect(url_for('owner.dashboard'))
    return render_template('owner/update_fuel.html', fuel=fuel)
