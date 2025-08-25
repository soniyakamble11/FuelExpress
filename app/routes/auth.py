from flask import current_app
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from app.utils.forms import LoginForm, RegistrationForm, AddressForm, OrderFuelForm   
from app import mail
from flask_mail import Message
from datetime import datetime, timedelta
import random
from app.models.fuel import FuelType
from app.models.address import Address
from app.models.order import Order, OrderStatus

bp = Blueprint("auth", __name__, url_prefix="/auth")

# ----------- LOGIN -----------
@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_verified:
                flash("Please verify your email before logging in.", "warning")
                return redirect(url_for("auth.login"))

            login_user(user, remember=form.remember_me.data)
            flash("Login successful!", "success")

            if user.is_customer():
                return redirect(url_for("customer.dashboard"))
            elif user.is_station_owner():
                return redirect(url_for('owner.dashboard'))  # station owner dashboard
            elif user.is_delivery_partner():
                return redirect(url_for('delivery.dashboard'))
            elif user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

    # For GET requests, just render login form
    return render_template("auth/login.html", form=form)



# ----------- LOGOUT -----------
@bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))

# ----------- REGISTER -----------
@bp.route("/register", methods=["GET", "POST"])
def register():
    print("\n" + "="*50)
    print(f"REGISTER ROUTE HIT - Method: {request.method}")
    print("="*50)
    
    form = RegistrationForm()
    
    if request.method == 'POST':
        print("🔥 POST REQUEST DETECTED!")
        print(f"Form data: {dict(request.form)}")
        print(f"Form validates: {form.validate_on_submit()}")
        
        if form.errors:
            print(f"❌ Form errors: {form.errors}")
        
        if form.validate_on_submit():
            print("✅ Form validation passed!")
            # Your existing OTP and user creation code...
            otp = f"{random.randint(100000, 999999)}"
            otp_expiry = datetime.utcnow() + timedelta(minutes=10)

            user = User(
                username=form.username.data,
                email=form.email.data,
                phone=form.phone.data,
                role=form.role.data,
                otp_code=otp,
                otp_expiry=otp_expiry,
                is_verified=False
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            print(f"👤 User created: {user.email}")
            
            # Send OTP Email
            try:
                msg = Message(
    "Verify Your Account - FuelExpress",
    sender=current_app.config['MAIL_USERNAME'],  # This line is crucial!
    recipients=[user.email],
    body=f"Hello {user.username},\n\nYour OTP is: {otp}\nIt expires in 10 minutes.\n\nThank you,\nFuelExpress Team"
)
                mail.send(msg)
                print("📧 Email sent successfully!")
            except Exception as e:
                print(f"❌ Email error: {e}")

            flash("OTP sent to your email. Please verify your account.", "info")
            return redirect(url_for("auth.verify", email=user.email))
        else:
            print("❌ Form validation failed!")
            print(f"Errors: {form.errors}")

    print("📄 Rendering register.html")
    return render_template("auth/register.html", form=form)

# ----------- SEED DATA FOR CUSTOMER DASHBOARD -----------
@bp.route("/seed-data")
def seed_data():
    """Seed initial fuel types and sample data for customer dashboard"""
    try:
        # Add fuel types
        fuel_types = [
            {'name': 'Petrol', 'price': 102.50, 'description': 'Premium unleaded petrol for cars and bikes'},
            {'name': 'Diesel', 'price': 89.75, 'description': 'High-speed diesel for trucks and cars'},
            {'name': 'CNG', 'price': 75.20, 'description': 'Compressed Natural Gas - eco-friendly option'}
        ]
        
        added_count = 0
        for fuel_data in fuel_types:
            existing = FuelType.query.filter_by(name=fuel_data['name']).first()
            if not existing:
                fuel = FuelType(
                    name=fuel_data['name'], 
                    price_per_liter=fuel_data['price'],
                    description=fuel_data['description']
                )
                db.session.add(fuel)
                added_count += 1
                print(f"✅ Added fuel type: {fuel_data['name']}")
        
        db.session.commit()
        
        # Get counts
        fuel_count = FuelType.query.count()
        user_count = User.query.count()
        address_count = Address.query.count()
        order_count = Order.query.count()
        
        return f"""
        <div style="font-family: Arial, sans-serif; padding: 30px; max-width: 800px; margin: 0 auto; background: #f8f9fa; min-height: 100vh;">
            <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="color: #28a745; text-align: center; margin-bottom: 30px;">
                    🎉 FuelExpress Database Seeded Successfully!
                </h1>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="margin: 0 0 15px 0;">📊 Database Status Overview</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 6px;">
                            <div style="font-size: 24px; font-weight: bold;">{fuel_count}</div>
                            <div>Fuel Types Available</div>
                            <div style="font-size: 12px; opacity: 0.8;">({added_count} newly added)</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 6px;">
                            <div style="font-size: 24px; font-weight: bold;">{user_count}</div>
                            <div>Registered Users</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 6px;">
                            <div style="font-size: 24px; font-weight: bold;">{address_count}</div>
                            <div>Saved Addresses</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 6px;">
                            <div style="font-size: 24px; font-weight: bold;">{order_count}</div>
                            <div>Total Orders</div>
                        </div>
                    </div>
                </div>
                
                <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                    <h3 style="color: #155724; margin: 0 0 15px 0;">🚛 Available Fuel Types & Pricing</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                        {''.join([f'''
                        <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #c3e6cb;">
                            <h4 style="margin: 0 0 5px 0; color: #155724; display: flex; align-items: center;">
                                {"⛽" if fuel.name == "Petrol" else "🚛" if fuel.name == "Diesel" else "🌿"} {fuel.name}
                            </h4>
                            <div style="font-size: 18px; font-weight: bold; color: #28a745; margin: 5px 0;">{fuel.formatted_price}/Liter</div>
                            <div style="font-size: 13px; color: #6c757d;">{fuel.description}</div>
                        </div>
                        ''' for fuel in FuelType.get_available_fuels()])}
                    </div>
                </div>
                
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <h3 style="color: #856404; margin: 0 0 10px 0;">🚀 Next Steps</h3>
                    <p style="margin: 5px 0; color: #856404;">Your FuelExpress app is now ready for:</p>
                    <ul style="color: #856404; margin: 10px 0;">
                        <li>✅ Customer Registration & Login</li>
                        <li>✅ Email OTP Verification</li>
                        <li>✅ Fuel Type Management</li>
                        <li>🔄 Customer Dashboard (Next: Order fuel, view history)</li>
                        <li>🔄 Address Management</li>
                        <li>🔄 Order Tracking System</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="/auth/list-users" style="background: linear-gradient(45deg, #007bff, #0056b3); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 0 10px; display: inline-block; font-weight: bold;">
                        👥 View All Users
                    </a>
                    <a href="/" style="background: linear-gradient(45deg, #28a745, #1e7e34); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 0 10px; display: inline-block; font-weight: bold;">
                        🏠 Go to Dashboard
                    </a>
                </div>
                
                <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <small style="color: #6c757d;">
                        🛠️ Database is ready for customer dashboard development!<br>
                        Next: Create customer dashboard, order forms, and address management.
                    </small>
                </div>
            </div>
        </div>
        """
    
    except Exception as e:
        db.session.rollback()
        return f"""
        <div style="font-family: Arial, sans-serif; padding: 30px; max-width: 600px; margin: 0 auto;">
            <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; border: 1px solid #f5c6cb;">
                <h2>❌ Error Seeding Database</h2>
                <p><strong>Error Details:</strong> {str(e)}</p>
                <div style="background: #fff; padding: 15px; border-radius: 6px; margin: 15px 0; color: #212529;">
                    <h4>🔧 Troubleshooting Steps:</h4>
                    <ol>
                        <li><strong>Run database migration first:</strong>
                            <code style="background: #f8f9fa; padding: 2px 6px; border-radius: 3px;">flask db migrate -m "Add customer dashboard models"</code>
                        </li>
                        <li><strong>Apply the migration:</strong>
                            <code style="background: #f8f9fa; padding: 2px 6px; border-radius: 3px;">flask db upgrade</code>
                        </li>
                        <li><strong>Make sure all model files are created in the models/ folder</strong></li>
                        <li><strong>Check that imports are working correctly</strong></li>
                    </ol>
                </div>
                <a href="/auth/list-users" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    👥 View Users
                </a>
            </div>
        </div>
        """

# ----------- DEBUG ROUTES (Remove in production) -----------
@bp.route("/get-otp/<email>")
def get_otp(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return f"<h1>OTP: {user.otp_code}</h1><p>Expires: {user.otp_expiry}</p>"
    return "User not found"

@bp.route("/list-users")
def list_users():
    users = User.query.all()
    if not users:
        return "<h1>No users found in database!</h1>"
    
    result = """
    <div style="font-family: Arial; padding: 20px; max-width: 800px; margin: 0 auto;">
        <h1>👥 All Registered Users</h1>
    """
    
    for user in users:
        verified_badge = "✅ Verified" if user.is_verified else "⏳ Pending"
        role_emoji = {"customer": "🛒", "delivery_partner": "🚛", "station_owner": "⛽", "admin": "👑"}.get(user.role, "👤")
        
        result += f"""
        <div style="background: white; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;">
            <h3>{role_emoji} {user.username}</h3>
            <p><strong>Email:</strong> {user.email} | <strong>Phone:</strong> {user.phone}</p>
            <p><strong>Role:</strong> {user.role.title()} | <strong>Status:</strong> {verified_badge}</p>
            <p><strong>Created:</strong> {user.created_at.strftime('%d %b %Y, %I:%M %p')}</p>
            <small><a href="/auth/delete-user/{user.email}" style="color: #dc3545;">🗑️ Delete User</a></small>
        </div>
        """
    
    result += f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="/auth/seed-data" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 0 10px;">🌱 Seed Data</a>
            <a href="/auth/clear-all-users" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 0 10px;">🗑️ Clear All</a>
        </div>
    </div>
    """
    return result

@bp.route("/refresh-otp/<email>")
def refresh_otp(email):
    user = User.query.filter_by(email=email).first()
    if user:
        # Generate new OTP with fresh expiry
        new_otp = f"{random.randint(100000, 999999)}"
        user.otp_code = new_otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        
        return f"<h1>New OTP: {new_otp}</h1><p>Expires: {user.otp_expiry}</p><p><a href='/auth/verify?email={email}'>Go to verification page</a></p>"
    return "User not found"

@bp.route("/delete-user/<email>")
def delete_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        return f"<h1>✅ Deleted user: {username} ({email})</h1><p><a href='/auth/list-users'>View remaining users</a></p>"
    return f"<h1>❌ User not found: {email}</h1>"

@bp.route("/clear-all-users")
def clear_all_users():
    count = User.query.count()
    User.query.delete()
    db.session.commit()
    return f"<h1>🗑️ Deleted {count} users from database</h1><p><a href='/auth/list-users'>View users (should be empty)</a></p>"

# ----------- VERIFY OTP -----------
@bp.route("/verify", methods=["GET", "POST"])
def verify():
    email = request.args.get("email")
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("auth.register"))

    if request.method == "POST":
        otp_input = request.form.get("otp")
        if user.otp_code == otp_input and datetime.utcnow() <= user.otp_expiry:
            user.is_verified = True
            user.otp_code = None
            user.otp_expiry = None
            db.session.commit()
            flash("Account verified! You can now log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Invalid or expired OTP. Please try again.", "danger")

    return render_template("auth/verify.html", email=email)



@bp.route('/addresses/add', methods=['GET', 'POST'])
@login_required
def add_address():
    form = AddressForm()

    if form.validate_on_submit():
        try:
            if form.is_default.data:
                Address.query.filter_by(user_id=current_user.id, is_default=True)\
                    .update({'is_default': False})

            new_address = Address(
                user_id=current_user.id,
                name=form.name.data,
                phone=form.phone.data,
                address_line1=form.address_line1.data,
                address_line2=form.address_line2.data,
                city=form.city.data,
                state=form.state.data,
                pincode=form.pincode.data,
                is_default=form.is_default.data
            )
            db.session.add(new_address)
            db.session.commit()
            flash('Address added successfully!', 'success')
            return redirect(url_for('customer.addresses'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while adding the address: {str(e)}", 'danger')
            print(f"Address Add Error: {e}")  # This will print the exact error in terminal

    return render_template('customer/add_address.html', form=form)

@bp.route('/order_fuel', methods=['GET', 'POST'])
@login_required
def order_fuel():
    form = OrderFuelForm()
    
    # Populate dropdowns
    form.fuel_id.choices = [(str(f.id), f"{f.name}") for f in FuelType.query.all()]
    form.address_id.choices = [(str(a.id), a.name) for a in Address.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        try:
            # Save order to DB
            order = Order(
                user_id=current_user.id,
                fuel_id=int(form.fuel_id.data),
                quantity=form.quantity.data,
                address_id=int(form.address_id.data),
                delivery_date=form.delivery_date.data,
                delivery_time=form.delivery_time.data,
                special_instructions=form.special_instructions.data,
                status=OrderStatus.PENDING
            )
            db.session.add(order)
            db.session.commit()
            flash("Order placed successfully!", "success")
            return redirect(url_for('customer.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while placing the order: {str(e)}", "danger")
            print(f"Order Error: {e}")

    return render_template('customer/order_fuel.html', form=form)
