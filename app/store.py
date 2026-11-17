from __future__ import annotations
import json
import sqlite3
from pathlib import Path

from datetime import datetime, timezone
from threading import Lock

from .pricing import add_days, calculate_quote, today_iso
from .security import hash_password


_CAR_IMAGES = {
    1: "/static/cars/axio.jpg",
    2: "/static/cars/demio.jpg",
    3: "/static/cars/aqua.jpg",
    4: "/static/cars/prado.jpg",
    5: "/static/cars/forester.jpg",
    6: "/static/cars/xtrail.jpg",
    7: "/static/cars/e-class.jpg",
    8: "/static/cars/bmw-5-series.jpg",
    9: "/static/cars/velar.jpg",
    10: "/static/cars/hiace.jpg",
}


def _img_for(category_id: int, car_id: int | None = None) -> str:
    if car_id and car_id in _CAR_IMAGES:
        return _CAR_IMAGES[car_id]
    return {
        1: "/static/cars/axio.jpg",
        2: "/static/cars/prado.jpg",
        3: "/static/cars/e-class.jpg",
        4: "/static/cars/hiace.jpg",
    }.get(category_id, "/static/cars/prado.jpg")


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
            "id": i,
            "category_id": cid,
            "make": mk,
            "model": mdl,
            "year": yr,
            "registration_number": reg,
            "color": color,
            "transmission": trans,
            "fuel_type": fuel,
            "seats": seats,
            "daily_rate": rate,
            "mileage": mileage,
            "status": status,
            "primary_image_url": _img_for(cid, i),
            "created_at": now,
        }

    cars = [
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
            "id": 1,
            "full_name": "Wanjiru Kamau",
            "email": "wanjiru@example.co.ke",
            "phone": "+254 712 345 678",
            "role": "customer",
            "password_hash": hash_password("demo1234"),
            "licence_number": "DL-0048213",
            "licence_expiry": add_days(t, 900),
            "is_active": True,
            "created_at": now,
        },
        {
            "id": 2,
            "full_name": "Admin",
            "email": "admin@lasquadradoro.co.ke",
            "phone": "+254 700 000 001",
            "role": "admin",
            "password_hash": hash_password("demo1234"),
            "licence_number": None,
            "licence_expiry": None,
            "is_active": True,
            "created_at": now,
        },
        {
            "id": 3,
            "full_name": "Otieno Ouma",
            "email": "otieno@example.co.ke",
            "phone": "+254 722 111 222",
            "role": "customer",
            "password_hash": hash_password("demo1234"),
            "licence_number": "DL-0099120",
            "licence_expiry": add_days(t, 600),
            "is_active": True,
            "created_at": now,
        },
    ]

    bookings: list[dict] = []
    seq = 1040
    booking_id = 0

    def mk(user, car_id, s_off, e_off, status, extra_ids=None, extra=None):
        nonlocal seq, booking_id
        extra_ids = extra_ids or []
        extra = extra or {}
        c = next(x for x in cars if x["id"] == car_id)
        ex = [e for e in extras if e["id"] in extra_ids]
        start = add_days(t, s_off)
        end = add_days(t, e_off)
        q = calculate_quote(c["daily_rate"], start, end, ex)
        seq += 1
        booking_id += 1
        bookings.append({
            "id": booking_id,
            "reference": f"LSD-{seq}",
            "user_id": user["id"],
            "car_id": car_id,
            "start_date": start,
            "end_date": end,
            "actual_return_date": extra.get("actual_return_date"),
            "pickup_location": "JKIA - Jomo Kenyatta Intl. Airport",
            "daily_rate_snapshot": c["daily_rate"],
            "days": q["days"],
            "subtotal": q["subtotal"],
            "extras_total": q["extras_total"],
            "extras": ex,
            "tax": q["tax"],
            "total_amount": q["total_amount"],
            "deposit": q["deposit"],
            "status": status,
            "pickup_mileage": extra.get("pickup_mileage"),
            "return_mileage": extra.get("return_mileage"),
            "cancelled_at": None,
            "created_at": now,
        })

    cust = users[0]
    other = users[2]
    mk(cust, 4, -20, -15, "completed", [2], {
        "pickup_mileage": 40200,
        "return_mileage": 41000,
        "actual_return_date": add_days(t, -15),
    })
    mk(other, 7, -2, 3, "active", [], {"pickup_mileage": 18100})
    mk(other, 5, -4, 1, "active", [1], {"pickup_mileage": 57200})
    mk(cust, 1, 3, 7, "confirmed", [1, 2])
    mk(other, 9, 5, 9, "pending", [3])
    mk(cust, 8, 12, 15, "pending")

    return {
        "users": users,
        "categories": categories,
        "cars": cars,
        "extras": extras,
        "bookings": bookings,
        "seq": seq,
    }


_store: dict | None = None
DB_PATH = Path(__file__).resolve().parent.parent / "la_squadra_doro.db"

_lock = Lock()


def save_store() -> None:
    store = get_store()
    db = sqlite3.connect(DB_PATH)
    try:
        with _lock, db:
            
            for c in store["cars"]:
                color_val = c.get("colour") or c.get("color") or "White"
                db.execute("""
                    INSERT OR REPLACE INTO cars 
                    (id, category_id, make, model, year, registration_number, colour, color, transmission, fuel_type, seats, daily_rate, mileage, status, primary_image_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    c["id"], c["category_id"], c["make"], c["model"], c["year"],
                    c["registration_number"], color_val, color_val,
                    c.get("transmission", "automatic"), c.get("fuel_type", "petrol"),
                    c.get("seats", 5), c["daily_rate"], c.get("mileage", 0),
                    c.get("status", "available"), c.get("primary_image_url", ""),
                    c.get("created_at")
                ))

            
            for b in store["bookings"]:
                extras_json = json.dumps(b.get("extras", [])) if isinstance(b.get("extras"), (list, dict)) else str(b.get("extras") or "[]")
                db.execute("""
                    INSERT OR REPLACE INTO bookings 
                    (id, reference, user_id, car_id, pickup_location, start_date, end_date, actual_return_date, daily_rate_snapshot, days, subtotal, extras_total, extras, tax, total_amount, deposit, status, pickup_mileage, return_mileage, cancelled_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    b["id"], b["reference"], b["user_id"], b["car_id"],
                    b.get("pickup_location", "JKIA - Nairobi Hub"),
                    b["start_date"], b["end_date"], b.get("actual_return_date"),
                    b.get("daily_rate_snapshot", 0), b.get("days", 1),
                    b.get("subtotal", 0), b.get("extras_total", 0), extras_json,
                    b.get("tax", 0), b.get("total_amount", 0), b.get("deposit", 0),
                    b.get("status", "pending"), b.get("pickup_mileage"),
                    b.get("return_mileage"), b.get("cancelled_at"), b.get("created_at")
                ))

            
            for u in store["users"]:
                pwd = u.get("password_hash") or u.get("hashed_password") or ""
                db.execute("""
                    INSERT OR REPLACE INTO users 
                    (id, full_name, email, phone, hashed_password, password_hash, role, licence_number, licence_expiry, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    u["id"], u["full_name"], u["email"], u["phone"],
                    pwd, pwd, u.get("role", "customer"),
                    u.get("licence_number"), u.get("licence_expiry"),
                    int(bool(u.get("is_active", True))), u.get("created_at")
                ))

            db.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('seq', ?)", (store["seq"],))
    finally:
        db.close()


def _load() -> dict | None:
    if not DB_PATH.exists():
        return None
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        categories = [dict(r) for r in db.execute("SELECT * FROM categories")]
        users = [dict(r) for r in db.execute("SELECT * FROM users")]
        for u in users:
            if not u.get("password_hash") and u.get("hashed_password"):
                u["password_hash"] = u["hashed_password"]
            u["is_active"] = bool(u.get("is_active"))

        cars = [dict(r) for r in db.execute("SELECT * FROM cars")]
        for c in cars:
            if not c.get("color") and c.get("colour"):
                c["color"] = c["colour"]
            elif not c.get("colour") and c.get("color"):
                c["colour"] = c["color"]
            if not c.get("primary_image_url"):
                c["primary_image_url"] = _img_for(c.get("category_id", 1), c.get("id"))

        extras = [dict(r) for r in db.execute("SELECT * FROM extras")]
        for e in extras:
            if "price" not in e and "price_per_day" in e:
                e["price"] = e["price_per_day"]
            if "per_day" not in e and "is_flat_rate" in e:
                e["per_day"] = not bool(e["is_flat_rate"])
            else:
                e["per_day"] = bool(e.get("per_day"))

        bookings = [dict(r) for r in db.execute("SELECT * FROM bookings")]
        for b in bookings:
            if isinstance(b.get("extras"), str):
                try:
                    b["extras"] = json.loads(b["extras"])
                except Exception:
                    b["extras"] = []
            elif not b.get("extras"):
                b["extras"] = []

        meta_row = db.execute("SELECT value FROM meta WHERE key='seq'").fetchone()
        seq = meta_row[0] if meta_row else 1050

        return {
            "users": users,
            "categories": categories,
            "cars": cars,
            "extras": extras,
            "bookings": bookings,
            "seq": seq,
        }
    except Exception as e:
        return None
    finally:
        db.close()


def get_store() -> dict:
    global _store
    if _store is None:
        with _lock:
            if _store is None:
                _store = _load() or _seed()
    return _store


def reset_store() -> None:
    global _store
    with _lock:
        _store = _seed()
    save_store()