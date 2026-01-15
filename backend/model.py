from sqlalchemy import create_engine, insert, update, delete, select, UniqueConstraint,DateTime, join
from sqlalchemy import Table, Column,Integer, String, ForeignKey,Numeric, MetaData,Float, func 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import  Mapped,mapped_column, DeclarativeBase, relationship
import sqlite3
import os
from typing import Optional, List
from sqlalchemy.orm import sessionmaker




# Now you can use the sqlite3 module and its functionality in your code

class Base(DeclarativeBase):
    pass

print(Base)
# Define the user model
class User(Base):
    __tablename__ = "user"

    id = mapped_column(Integer, primary_key=True)
    full_names = mapped_column(String(255))
    username = mapped_column(String(255))
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    password_hash = mapped_column(String(1000))
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")
    portfolio: Mapped["Portfolio"] = relationship(back_populates="user")
    cash: Mapped[int] = mapped_column(insert_default=10000)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
 
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
 
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Address(Base):
    __tablename__ = "address"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
 


class Portfolio(Base):
    __tablename__ = 'portfolio'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user: Mapped["User"] = relationship(back_populates="portfolio")
    symbol = Column(String(15))
    quantity = Column(Integer)
    price = Column(Float)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    symbol = Column(String(15))
    quantity = Column(Integer)
    price = Column(Float)
    transaction_type = Column(String(10))  # 'BUY' or 'SELL'
    timestamp = Column(DateTime, default=func.now())


DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///finance.db')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # This creates all your classes (User, Portfolio, etc.) as tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully in 'finance_app'!")

# Use this to get a session whenever you need to add data
def dbconnect():
    return SessionLocal()
