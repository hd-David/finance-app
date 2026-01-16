from sqlalchemy import String, ForeignKey, Float, DateTime, func, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, sessionmaker
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import List
import os

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_names: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(1000))
    cash: Mapped[float] = mapped_column(Numeric(15, 2), insert_default=10000.00)
    create_date: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    portfolio: Mapped[List["Portfolio"]] = relationship(back_populates="user")
    
    __table_args__ = (
        # Basic DB-level check to ensure email has an '@'
        CheckConstraint("email LIKE '%@%'", name="user_email_check"),
    )
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        # This MUST set the actual column name 'password_hash'
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Portfolio(Base):
    __tablename__ = 'portfolio'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    symbol: Mapped[str] = mapped_column(String(15))
    quantity: Mapped[int] = mapped_column()
    price: Mapped[float] = mapped_column(Numeric(10, 2)) # Purchase price

    user: Mapped["User"] = relationship(back_populates="portfolio")

class Transaction(Base):
    __tablename__ = 'transactions'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    symbol: Mapped[str] = mapped_column(String(15))
    quantity: Mapped[int] = mapped_column()
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    transaction_type: Mapped[str] = mapped_column(String(10)) # 'BUY' or 'SELL'
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())



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
