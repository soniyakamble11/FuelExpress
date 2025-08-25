from flask import Blueprint, render_template, request, current_app

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Homepage"""
    # Temporarily remove fuel stations until we create the model
    return render_template('index.html')

@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@bp.route('/how-it-works')
def how_it_works():
    """How it works page"""
    return render_template('how_it_works.html')