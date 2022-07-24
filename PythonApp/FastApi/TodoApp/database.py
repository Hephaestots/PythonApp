from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

# Engine
alchemy_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session local instance
# Using sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=alchemy_engine)

# Declarative base
Base = declarative_base()


