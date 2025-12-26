# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings

# # Create the Database Engine
# engine = create_engine(settings.DATABASE_URL)

# # Create a Session Factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base class for models
# Base = declarative_base()

# def get_db():
#     """Dependency for FastAPI Routes"""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()