from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance, imported by models.py and app.py
db = SQLAlchemy()
