from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Date, BigInteger, SmallInteger
from sqlalchemy.orm import relationship

from db import Base
from db.utils import CreatedModel


# ctrl + space*2
class User(CreatedModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True,unique=True)
    name = Column(String)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    jinsi = Column(String(50), nullable=True)  # 'erkak' yoki 'ayol'
    created_at = Column(DateTime, default=datetime.utcnow)
    driver = relationship("Driver", back_populates="user", uselist=False)
    driver_id = Column(BigInteger, ForeignKey("drivers.id"))


# 2️⃣ Haydovchilar jadvali (faqat haydovchilar uchun maxsus)
class Driver(CreatedModel):
    __tablename__ = "drivers"

    id = Column(BigInteger, primary_key=True,unique=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    car_model = Column(String(255), nullable=False)
    car_number = Column(String(20), nullable=False)
    permission_date = Column(DateTime, default=datetime.now()+timedelta(days=30))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foydalanuvchi bilan bog'lanish
    user = relationship("User", back_populates="driver")



# 3️⃣ Adminlar jadvali
class Admin(CreatedModel):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Hashlangan parol
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(CreatedModel):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    driver_id = Column(BigInteger, ForeignKey("drivers.id", ondelete="SET NULL"),
                       nullable=True,default=None)  # Agar haydovchi topilmasa, NULL bo‘lishi mumkin
    dropoff_location = Column(String(255), nullable=False)  # Manzil
    status = Column(String(20), nullable=False, default="pending")  # pending, accepted, completed, cancelled
    yuk = Column(String(255), nullable=True)
    order_type = Column(String(50), nullable=False)
    sana = Column(String(5))
    count = Column(SmallInteger, nullable=True,default=0)
    driver_visit_count = Column(SmallInteger, nullable=True,default=0)




    # Bog‘lanishlar
    passenger = relationship("User", backref="orders")
    driver = relationship("Driver", backref="orders")
    messages = relationship("OrderMessage", lazy='dynamic')



class OrderMessage(CreatedModel):
    __tablename__ = "order_messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    message_id=Column(String(255), nullable=True)

    user = relationship("User", backref="messages")
metadata = Base.metadata