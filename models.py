from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from database import Base
import bcrypt

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer)
    price_per_day = Column(Float)
    transmission = Column(String)  # manual / automatic
    fuel_type = Column(String)     # petrol / diesel / electric / hybrid
    seats = Column(Integer, default=5)
    is_available = Column(Boolean, default=True)
    image_url = Column(String, default="/static/img/car-placeholder.jpg")
    latitude = Column(Float, default=55.751244)   # Москва
    longitude = Column(Float, default=37.618423)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    car_id = Column(Integer, ForeignKey("cars.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    total_price = Column(Float)
    status = Column(String, default="pending")  # pending, paid, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
