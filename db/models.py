from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Date, Float
from sqlalchemy.orm import relationship

from db import Base


# ctrl + space*2
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    jinsi = Column(String(10), nullable=False)  # 'driver' yoki 'passenger'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Haydovchi bilan bog'lanish
    driver = relationship("Driver", back_populates="user", uselist=False)


# 2️⃣ Haydovchilar jadvali (faqat haydovchilar uchun maxsus)
class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Hashlangan parol saqlanadi
    car_model = Column(String(255), nullable=False)
    car_number = Column(String(20), unique=True, nullable=False)
    access_until = Column(Date, nullable=True)  # Botdan foydalanish muddati
    is_approved = Column(Boolean, default=False)  # Admin tasdiqlashi kerak
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foydalanuvchi bilan bog'lanish
    user = relationship("User", back_populates="driver")


# 3️⃣ Adminlar jadvali
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Hashlangan parol
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"),
                       nullable=True)  # Agar haydovchi topilmasa, NULL bo‘lishi mumkin
    pickup_location = Column(String(255), nullable=False)  # Qayerdan olib ketish
    dropoff_location = Column(String(255), nullable=False)  # Manzil
    price = Column(Float, nullable=False)  # Narx
    status = Column(String(20), nullable=False, default="pending")  # pending, accepted, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    # Bog‘lanishlar
    passenger = relationship("User", backref="orders")
    driver = relationship("Driver", backref="orders")


metadata = Base.metadata