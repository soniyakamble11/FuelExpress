from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')