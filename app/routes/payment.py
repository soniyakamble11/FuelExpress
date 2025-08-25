from flask import render_template, request, redirect, url_for, flash, Blueprint
from app.models.order import Order, OrderStatus
from app.utils.forms import PaymentForm
from app import db

bp = Blueprint('payment', __name__, url_prefix="/payment")

@bp.route('/pay/<order_id>', methods=['GET', 'POST'])
def pay(order_id):
    order = Order.query.filter_by(order_number=order_id).first_or_404()
    form = PaymentForm()

    if form.validate_on_submit():  # checks CSRF automatically
        if form.payment_mode.data == 'COD':
            order.status = OrderStatus.CONFIRMED
            db.session.commit()
            flash('COD selected. Your order is confirmed!', 'success')
        else:
            # handle online payment logic here
            flash('Online payment selected. Redirecting...', 'info')

        # after payment, redirect to success page
        return redirect(url_for('payment.success', order_id=order.order_number))

    return render_template('payment/pay.html', order=order, form=form)


@bp.route('/success/<order_id>')
def success(order_id):
    order = Order.query.filter_by(order_number=order_id).first_or_404()
    return render_template('payment/success.html', order=order)
