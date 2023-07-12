from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Phone_book(Base):
    __tablename__ = 'phone_book'
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index= True)
    tel = Column(String)
    email = Column(String)
    
