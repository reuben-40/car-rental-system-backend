from __future__ import annotations

from datetime import date, datetime
from threading import Lock
from time import timezone

from .pricing import add_days, calculate_quote, today_iso
from .security import hash_password

# Car images from Pexels (real, guaranteed-to-load URLs).
_IMG_ECONOMY = "https://images.pexels.com/photos/32422135/pexels-photo-32422135.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
_IMG_LUXURY = "https://images.pexels.com/photos/10638649/pexels-photo-10638649.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
_IMG_SUV = "https://images.pexels.com/photos/13365861/pexels-photo-13365861.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
_IMG_VAN = "https://images.pexels.com/photos/19548262/pexels-photo-19548262.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"


def _img_for(category_id: int) -> str:
    return {1: _IMG_ECONOMY, 2: _IMG_SUV, 3: _IMG_LUXURY, 4: _IMG_VAN}.get(category_id, _IMG_SUV)

# typed dicts - the store uses plain dicts so pydantic can adapt them.
# Each "model" dict mirrors a schema in schemas.py.

def _seed() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    t = today_iso()

    categories = [
        {"id": 1, "name": "Economy", "description": "Fuel-sipping city cars"},
        {"id": 2, "name": "SUV", "description": "Safari-ready 4x4s"},
        {"id": 3, "name": "Luxury", "description": "Executive arrivals"},
        {"id": 4, "name": "Van", "description": "Groups and cargo"},
    ]

    extras = [
        {"id": 1, "name": "Child seat", "description": "ISOFIX, ages 1-4", "price": 500, "per_day": True},
        {"id": 2, "name": "GPS navigation", "description": "offline Kenya maps", "price": 400, "per_day": True},
        {"id": 3, "name": "Extra driver", "description": "Add a second licensed driver", "price": 2500, "per_day": False},
    ]

    def car(i, cid, mk, mdl, yr, reg, color, trans, fuel, seats, rate, mileage, status="available"):
        return {
            "id": i, "category_id": cid, "make": mk, "model":mdl, "year": yr,
            "registration_number": reg, "color": color, "transmission": trans,
            "fuel_type": fuel, "seats": seats, "daily_rate": rate, "mileage": mileage, 
            "status": status, "primary_image_url": _img_for(cid), "created_at": now,      
        }

    cars =[
        car(1, 1, "Toyota", "Axio", 2019, "KDK 214A", "White", "automatic", "petrol", 5, 4500, 61200),
        car(2, 1, "Mazda", "Demio", 2020, "KDM 882C", "Silver", "automatic", "petrol", 5, 3800, 48300),
        car(3, 1, "Toyota", "Aqua", 2021, "KDP 117F", "Blue", "automatic", "hybrid", 5, 4200, 33900),
        car(4, 2, "Toyota", "Land Cruiser Prado", 2022, "KDS 450G", "Forest green", "automatic", "diesel", 7, 14500, 41000),
        car(5, 2, "Subaru", "Forester", 2020, "KDN 309B", "Grey", "automatic", "petrol", 5, 8500, 57800),
        car(6, 2, "Nissan", "X-Trail", 2019, "KDJ 776D", "Black", "manual", "petrol", 7, 7800, 72100, "maintenance"),
        car(7, 3, "Mercedes-Benz", "E-Class", 2022, "KDT 001L", "Obsidian black", "automatic", "petrol", 5, 22000, 18500),
        car(8, 3, "BMW", "5 Series", 2021, "KDR 555X", "Carbon black", "automatic", "hybrid", 5, 20000, 26400),
        car(9, 3, "Range Rover", "Velar", 2023, "KDV 777X", "Santorini black", "automatic", "diesel", 5, 28000, 9800),
        car(10, 4, "Toyota", "HiAce", 2020, "KDL 640K", "White", "manual", "diesel", 14, 12000, 88200),
    ]

    users = [
        {
        "id": 1, "full_name": "Wanjiru kamau", "email": "wanjiru@example.co.ke",
        "phone": "+254 712 345 678", "role": "customer",
        "password_hash": hash_password("demo1234"),
        "licence_number": "DL-0048213", "licence_expiry": add_days(t, 900),
        "is_active": True, "created_at": now,
        },
        {
            "id": 2, "full_name": "Admin", "email": "admin@lasquadradoro.com",
            "phone": "+254 700 00 001", "role": "admin",
            "password_hash": hash_password("demo1234"),
            "licence_number": "None", "licence_expiry": None,
            "is_active": True, "created_at": now,
        },
        {
            "id": 3, "full_name": "otieno Ouma", "email": "otieno@example.com",
            "phone": "+254 722 111 222", "role": "customer",
            "password_hash": hash_password("demo1234"),
            "licence_number": "DL-0099120", "licence_expiry": add_days(t, 600),
            "is_active": True, "created_at": now,
        },
    ]

    bookings: list[dict] = []
    seq = 1040
    booking_id = 0

    def mk(user, car_id, s_off, e_off, status, extra_ids=None, extra=None):
        nonlocal seq, booking_id
        extra_ids = extra_ids or []
        extra = extra or {}
        c = next(x for x in cars if x ["id"] == car_id)
        ex = [e for e in extras if e["id"] in extra_ids]
        start = add_days(t, s_off)
        end = add_days(t, e_off)
        q = calculate_quote(c["daily_rate"], start, end, ex)
        seq += 1
        booking_id += 1
        bookings.append({
            "id": booking_id, "reference": f"LSD-{seq}", "user_id": user["id"],
            "car_id": car_id, "start_date": start, "end_date": end,
            "actual_return_date": extra.get("actual_return_date"),
            "pickup_location": "JKIA - Jomo Kenyatta Intl. Airport",
            "daily_rate_snapshot": c["daily_rate"], "days": q["days"],
            "subtotal": q["subtotal"], "extras_total": q["extras_total"],
            "extras": ex, "tax": q["tax"], "total_amount": q["total_amount"],
            "deposit": q["deposit"], "status": status,
            "pickup_mileage": extra.get("pickup_mileage"),
            "return_mileage": extra.get("return_mileage"),
            "cancelled_out": None, "created-at": now,
        })

        cust = users[0]
        other = users[2]
        mk(cust, 4, -20, "completed", [2],
           {"pickup_mileage": 40200, "return_mileage":41000, "actual_return_date": add_days(t, -15)})
        mk(other, 7, -2, 3, "active", [], {"pickup_mileage": 18100})
        mk(other, 5, -4, 1, "active", [1], {"pickup_mileage": 57200})
        mk(cust, 1, 3, 7, "confirmed", [1, 2])
        mk(other, 9,5,9, "pending", [3])
        mk(cust, 8, 12, 15, "pending")

        return {
            "users": users,
            "categories": categories,
            "cars": cars,
            "extras": extras,
            "bokings": bookings,
            "seq": seq,
        }

    from datetime import datetime, timezone 

    _store: dict | None = None
    _lock = Lock()

    def get_store() -> dict: 
        global _store
        if _store is None:
            with _lock:
                if _store is None:
                    _store = _seed()
        return _store

    def reset_store() -> None:
        global _store
        with _lock:
            _store = _seed()