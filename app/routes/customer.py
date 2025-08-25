from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf, validate_csrf
from app.models import db, User, FuelType, Address, Order, OrderStatus
from datetime import datetime, timedelta
from sqlalchemy import desc
from decimal import Decimal
from app.utils.forms import OrderFuelForm


bp = Blueprint('customer', __name__, url_prefix='/customer')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard overview"""
    total_orders = Order.query.filter_by(user_id=current_user.id).count()
    pending_orders = Order.query.filter_by(user_id=current_user.id, status=OrderStatus.PENDING).count()
    completed_orders = Order.query.filter_by(user_id=current_user.id, status=OrderStatus.DELIVERED).count()

    completed_orders_list = Order.query.filter_by(
        user_id=current_user.id, 
        status=OrderStatus.DELIVERED
    ).all()
    total_spent = sum(order.total_amount for order in completed_orders_list)

    recent_orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Order.created_at)).limit(5).all()

    fuel_types = FuelType.query.all()

    default_address = Address.query.filter_by(
        user_id=current_user.id, 
        is_default=True
    ).first()

    return render_template('customer/dashboard.html',
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           completed_orders=completed_orders,
                           total_spent=total_spent,
                           recent_orders=recent_orders,
                           fuel_types=fuel_types,
                           default_address=default_address)


@bp.route('/order-fuel', methods=['GET', 'POST'])
@login_required
def order_fuel():
    fuels = FuelType.query.all()
    addresses = Address.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        try:
            fuel_id = request.form.get("fuel_id")
            address_id = request.form.get("address_id")
            quantity = Decimal(request.form.get("quantity"))
            delivery_date = request.form.get("delivery_date")  # "YYYY-MM-DD"
            delivery_time = request.form.get("delivery_time")  # "HH:MM"
            special_instructions = request.form.get("special_instructions")

            fuel = FuelType.query.get(fuel_id)
            address = Address.query.get(address_id)

            if not fuel or not address:
                flash("Invalid fuel or address selection", "error")
                return redirect(url_for("customer.order_fuel"))

            # Ensure valid datetime
            delivery_datetime = datetime.combine(
                datetime.strptime(delivery_date, "%Y-%m-%d").date(),
                datetime.strptime(delivery_time, "%H:%M").time()
            )

            if delivery_datetime <= datetime.now() + timedelta(hours=2):
                flash("Delivery must be scheduled at least 2 hours from now!", "error")
                return redirect(url_for("customer.order_fuel"))

            # Price calculations
            price_per_liter = Decimal(fuel.price_per_liter)
            total_fuel_cost = quantity * price_per_liter
            delivery_fee = Decimal("50.00")  # example fixed fee
            total_amount = total_fuel_cost + delivery_fee

            # Generate unique order number
            order_number = f"ORD{int(datetime.utcnow().timestamp())}"

            new_order = Order(
                order_number=order_number,
                user_id=current_user.id,
                fuel_type_id=fuel.id,
                quantity_liters=quantity,
                price_per_liter=price_per_liter,
                total_fuel_cost=total_fuel_cost,
                delivery_address_id=address.id,
                delivery_date=datetime.strptime(delivery_date, "%Y-%m-%d").date(),
                delivery_time_slot=delivery_time,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                special_instructions=special_instructions,
                status="PENDING",
                created_at=datetime.utcnow()
            )

            db.session.add(new_order)
            db.session.commit()

            flash(f"Order placed successfully! Total: ₹{total_amount:.2f}", "success")
            # Redirect directly to payment page
            return redirect(url_for("payment.pay", order_id=new_order.order_number))

        except Exception as e:
            db.session.rollback()
            print("Order Error:", e)
            flash("Failed to place order. Please try again.", "error")

    return render_template("customer/order_fuel.html", fuels=fuels, addresses=addresses)
@bp.route('/order/<int:order_id>', methods=['GET'])
@login_required
def order_details(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template("customer/order_details.html", order=order)


@bp.route('/addresses')
@login_required
def addresses():
    """Manage delivery addresses"""
    user_addresses = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('customer/addresses.html', addresses=user_addresses)


@bp.route('/addresses/add', methods=['GET', 'POST'])
@login_required
def add_address():
    """Add a new delivery address"""
    if request.method == 'POST':
        try:
            name = request.form.get('name').strip()
            address_line1 = request.form.get('address_line1').strip()
            address_line2 = request.form.get('address_line2', '').strip()
            city = request.form.get('city').strip()
            state = request.form.get('state').strip()
            pincode = request.form.get('pincode').strip()
            phone = request.form.get('phone').strip()
            label = request.form.get('label', 'Home').strip()  # default label
            is_default = request.form.get('is_default') == 'on'

            if not all([name, address_line1, city, state, pincode, phone]):
                flash('All required fields must be filled!', 'error')
                return redirect(url_for('customer.add_address'))

            if is_default:
                Address.query.filter_by(user_id=current_user.id, is_default=True)\
                    .update({'is_default': False})

            new_address = Address(
                user_id=current_user.id,
                name=name,
                phone=phone,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                pincode=pincode,
                label=label,
                is_default=is_default
            )

            db.session.add(new_address)
            db.session.commit()

            flash('Address added successfully!', 'success')
            return redirect(url_for('customer.addresses'))

        except Exception as e:
            db.session.rollback()
            print("Address Add Error:", e)
            flash(f"An error occurred while adding the address: {e}", 'danger')

    return render_template('customer/add_address.html')


@bp.route('/addresses/<int:address_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    """Edit an existing delivery address"""
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        try:
            address.name = request.form.get('name').strip()
            address.phone = request.form.get('phone').strip()
            address.address_line1 = request.form.get('address_line1').strip()
            address.address_line2 = request.form.get('address_line2', '').strip()
            address.city = request.form.get('city').strip()
            address.state = request.form.get('state').strip()
            address.pincode = request.form.get('pincode').strip()
            address.label = request.form.get('label', 'Home').strip()
            address.is_default = request.form.get('is_default') == 'on'

            if address.is_default:
                Address.query.filter_by(user_id=current_user.id, is_default=True)\
                    .update({'is_default': False}, synchronize_session=False)

            db.session.commit()
            flash('Address updated successfully!', 'success')
            return redirect(url_for('customer.addresses'))

        except Exception as e:
            db.session.rollback()
            print("Address Edit Error:", e)
            flash(f"An error occurred while updating the address: {e}", 'danger')

    return render_template('customer/edit_address.html', address=address)


@bp.route('/addresses/<int:address_id>/delete', methods=['POST'])
@login_required
def delete_address(address_id):
    """Delete a delivery address"""
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    orders_count = Order.query.filter_by(delivery_address_id=address_id).count()

    if orders_count > 0:
        flash('Cannot delete address that has associated orders!', 'error')
    else:
        db.session.delete(address)
        db.session.commit()
        flash('Address deleted successfully!', 'success')

    return redirect(url_for('customer.addresses'))


@bp.route('/addresses/<int:address_id>/set-default', methods=['POST'])
@login_required
def set_default_address(address_id):
    """Set an address as default"""
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
    address.is_default = True
    db.session.commit()

    flash('Default address updated successfully!', 'success')
    return redirect(url_for('customer.addresses'))


@bp.route('/profile')
@login_required
def profile():
    """View and edit profile"""
    return render_template('customer/profile.html')


@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        current_user.name = request.form.get('name').strip()
        current_user.phone = request.form.get('phone').strip()

        if not all([current_user.name, current_user.phone]):
            flash('Name and phone are required!', 'error')
            return redirect(url_for('customer.profile'))

        db.session.commit()
        flash('Profile updated successfully!', 'success')

    except Exception as e:
        flash('An error occurred while updating your profile. Please try again.', 'error')
        db.session.rollback()

    return redirect(url_for('customer.profile'))


@bp.route('/api/fuel-price/<int:fuel_id>')
@login_required
def get_fuel_price(fuel_id):
    """API endpoint to get current fuel price"""
    fuel = FuelType.query.get_or_404(fuel_id)
    return jsonify({
        'price_per_liter': fuel.price_per_liter,
        'name': fuel.name,
        'description': fuel.description
    })

@bp.route('/orders')
@login_required
def orders_history():
    # fetch user orders from DB
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('customer/orders.html', orders=user_orders)

@bp.route("/create_order", methods=["POST"])
@login_required
def create_order():
    try:
        fuel_type_id = request.form.get("fuel_type_id")
        litres = request.form.get("litres")
        special_instructions = request.form.get("special_instructions")

        # Validate inputs
        if not fuel_type_id or not litres:
            flash("Please select a fuel type and enter litres", "danger")
            return redirect(url_for("main.order_fuel"))

        litres = float(litres)

        # Get fuel type details from DB
        fuel_type = FuelType.query.get(fuel_type_id)
        if not fuel_type:
            flash("Invalid fuel type selected", "danger")
            return redirect(url_for("main.order_fuel"))

        total_price = litres * fuel_type.price_per_litre

        # Create new order
        order = Order(
            user_id=current_user.id,
            fuel_type_id=fuel_type.id,   
            litres=litres,
            total_price=total_price,
            status="Pending",
            special_instructions=special_instructions
        )
        db.session.add(order)
        db.session.commit()

        flash("Order placed successfully!", "success")
        return redirect(url_for("main.order_history"))

    except Exception as e:
        db.session.rollback()
        flash(f"Failed to place order: {str(e)}", "danger")
        return redirect(url_for("main.order_fuel"))
