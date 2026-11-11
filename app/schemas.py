from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ROle:
    CUSTOMER = "customer"
    ADMIN = "admin"
    ALL = {"customer", "admin"}

class Transmission:
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    ALL = {"manual", "automatic"}

class FuelType:
    PETROL = "petrol"
    DIESEL = "diesel"
    HYBRID = "hybrid"
    ELECTRIC = "electric"
    ALL = {"petrol", "diesel", "hybrid", "electric"}

class CarStatus:
    AVAILABLE = "available"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"
    ALL = {"available", "maintenance", "retired"}

class BookingStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ALL = {"pending", "confirmed", "active", "completed", "cancelled"}
    BLOCKING = {"pending", "confirmed", "active"}



class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int 
    full_name: str
    email: EmailStr
    phone: str
    role: str
    licence_number: Optional[str] = None
    licence_expiry: Optional[str] = None
    is_active: bool
    created_at: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    licence_number: Optional[str] = None
    licence_expiry: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User



class Category(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str


class CarBase(BaseModel):
    category_id: int
    make: str
    model: str
    year: int
    registration_number: str
    color: str = ""
    transmission: str = "automatic"
    fuel_type: str = "petrol"
    seats: int = 5
    daily_rate: float
    mileage: int = 0
    status: str = "available"
    primary_image_url: str = ""


class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    category_id: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    registration_number: Optional[str] = None
    color: Optional[str] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    seats: Optional[int] = None
    daily_rate: Optional[float] = None
    mileage: Optional[int] = None
    status: Optional[str] = None
    primary_image_url: Optional[str] = None


class Car(CarBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: str
    category: Optional[Category] = None


class DateRange(BaseModel):
    start_date: str
    end_date: str


class CarDetail(Car):
    booked_ranges: list[DateRange] = []


class Paginated(BaseModel):
    items:list
    total: int
    page: int
    size: int



class Extra(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str = ""
    price: float
    per_day: bool = False



class QuoteRequest(BaseModel):
    car_id: int
    start_date: str
    end_date: str
    extra_ids: list[int] = []


class Quote(BaseModel):
    days: int
    daily_rate: float
    subtotal: float
    extras_total: float
    tax: float
    total_amount: float
    deposit: float


class BookingCreate(QuoteRequest):
    pickup_location: str



class Booking(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    reference: str
    user_id: int
    car_id: int
    car: Optional[Car] = None
    user: Optional[dict] = None
    start_date: str
    end_date: str
    actual_return_date: str
    pickup_location: str
    daily_rate_snapshot: float
    days: int
    subtotal: float
    extras_total: float
    extras: list[Extra] = []
    tax: float
    total_amount: float
    deposit: float
    status: str
    pickup_mileage: Optional[int] = None
    return_mileage: Optional[int] = None
    cancelled_at: Optional[str] = None 
    created_at: str



class Dashboard(BaseModel):
    cars_on_hire: int 
    monthly_revenue: float
    upcoming_returns: list[Booking] = []
    pending_bookings: int
    fleet_total: int
    fleet_available: int
    fleet_maintenance: int
    