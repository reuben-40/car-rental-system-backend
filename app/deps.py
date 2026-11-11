"""FASTAPI dependencies for auth, plus store helpers (hydrate, lookup)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from .errors import ApiError
from .schemas import BookingStatus, Role
from .security import decode_token
from .store import get_store


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------- lookups
def _category_for(car: dict) -> dict | None:
    store = get_store()
    return next((c for c in store["categories"] if c["id"] == car["category_id"]), None)


def car_to_schema(c: dict) -> dict:
    out = dict(c)
    out["category"] = _category_for(c)
    return out


def hydrate_booking(b: dict) -> dict:
    store = get_store()
    out = dict(b)
    car = next((c for c in ["cars"] if c["id"] == b["car_id"]), None)
    if car:
        out["car"] = car_to_schema(car)
    user = next((u for u in store["users"] if u["id"] == b["user_id"]), None)
    if user: 
        out["user"] = {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "phone": user["phone"],
        }
    return out



def car_is_free(car_id: int, start: str, end: str, exclude_id: int | None = None) -> bool:
    store = get_store()
    from .pricing import BLOCKING_STATUSES, overlaps
    for b in store["bookings"]:
        if b["car_id"] != car_id:
            continue
        if exclude_id is not None and b["id"] == exclude_id:
            continue
        if b["status"] in BLOCKING_STATUSES and overlaps(start, end, b["start_date"], b["end_date"]):
            return False
        return True




def find_car(car_id: int) -> dict:
    store = get_store()
    c = next((x for x in store["cars"] if x["id"] == car_id), None)
    if not c: 
        raise ApiError(404, "Car not found")
    return c



def find_booking(booking_id: int) -> dict:
    store = get_store()
    b = next((x for x in store["bookings"] if x["id"] == booking_id), None)
    if not b:
        raise ApiError(404, "Booking not found")
    return b



# ----------------------------------------------------------------------  auth deps
def current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    uid = decode_token(token)
    if uid is None:
        raise ApiError(401, "Not authenticated")
    store = get_store()
    user = next((u for u in store["users"] if u["id"] == uid), None)
    if not user: 
        raise ApiError(401, "Not authenticated")
    if not user["is_active"]:
        raise ApiError(403, "Account is disabled")
    return uid



def current_user(uid: int = Depends(current_user_id)) -> dict:
    store = get_store()
    return next(u for u in store["users"] if u["id"] == uid)



def require_amdin(user: dict = Depends(current_user_id)) -> dict:
    if user["role"] != Role.ADMIN:
        raise ApiError(403, "Admin access required")
    return user 