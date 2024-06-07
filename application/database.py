from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://postgres:pavilion%40%40%40@localhost/fastapi"

#Establishing connection with Postgres
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#Session- used to communicate with the database 

SessionLocal= sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


