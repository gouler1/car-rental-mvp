from pydantic import BaseModel
from datetime import date
from typing import Optional

# Auth
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# Car
class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    price_per_day: float
    transmission: str
    fuel_type: str
    seats: int = 5
    is_available: bool = True
    latitude: float = 55.751244
    longitude: float = 37.618423

class Car(CarBase):
    id: int
    image_url: str

    class Config:
        from_attributes = True

# Booking
class BookingCreate(BaseModel):
    car_id: int
    start_date: date
    end_date: date

class Booking(BaseModel):
    id: int
    car_id: int
    start_date: date
    end_date: date
    total_price: float
    status: str

    class Config:
        from_attributes = True
