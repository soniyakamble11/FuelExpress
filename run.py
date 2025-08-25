import os
from flask.cli import with_appcontext
from app import create_app, db

# Set environment variables for Flask
os.environ.setdefault('FLASK_APP', 'run.py')
os.environ.setdefault('FLASK_ENV', 'development')

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Make shell context available
@app.shell_context_processor
def make_shell_context():
    return {'db': db}

@app.cli.command()
@with_appcontext
def create_tables():
    """Create database tables."""
    db.create_all()
    print("Database tables created!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)