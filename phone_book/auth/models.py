from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from phone_book.database import Base

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    entries = relationship("Phone_book", back_populates="author")
    