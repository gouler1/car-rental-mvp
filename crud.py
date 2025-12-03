from sqlalchemy.orm import Session
from models import User, Car, Booking
from schemas import UserCreate, BookingCreate
from datetime import date

def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, full_name=user.full_name, phone=user.phone)
    db_user.set_password(user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_cars(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Car).offset(skip).limit(limit).all()

def get_car(db: Session, car_id: int):
    return db.query(Car).filter(Car.id == car_id).first()

def create_booking(db: Session, booking: BookingCreate, user_id: int):
    car = get_car(db, booking.car_id)
    days = (booking.end_date - booking.start_date).days
    if days <= 0:
        raise ValueError("End date must be after start date")
    total = days * car.price_per_day
    db_booking = Booking(
        user_id=user_id,
        car_id=booking.car_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        total_price=total,
        status="pending"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking
