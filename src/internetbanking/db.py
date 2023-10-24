import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from models import Base 
from datetime import timedelta
session_factory = sessionmaker(autoflush=True, bind=None)

session = scoped_session(session_factory) # mengkaitkan session dengan engine

def init(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('POSTGRES_URL')
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_KEY')
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)
    engine = create_engine("postgresql://postgres:admin123@localhost:5433/internetbanking")
    session.configure(bind=engine)
    Base.query=session.query_property()




