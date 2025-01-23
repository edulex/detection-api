from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

DATABASE_URL = "sqlite:///./app/data/database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    video_path = Column(String)
    audio_path = Column(String)
    handwriting_image_path = Column(String)
    status = Column(String, default="queued")  # queued, processing, completed, failed
    result = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)
