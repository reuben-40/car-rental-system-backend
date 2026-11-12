from fastapi import APIRouter, Depends

from ..deps import (car_is_free, current_user, find_booking, find_car,
                    hydrate_booking)
from ..errors import ApiError
from ..pricing import (BLOCKING_STATUSES, calculate_quote, today_iso,
                       validate_dates)
from ..schemas import Booking, BookingCreate, Quote, QuoteRequest
from ..store import get_store

router = APIRouter(prefix="/bookings", tags=["bookings"])



@router.post("/quote", response_model=Quote)
def quote(req: QuoteRequest):
    validate_dates(req.start_date, req.end_date)
    c = find_car(req.car_id)
    store = get_store()
    extras = [e for e in store["extras"] if e["id"] in req.extra_ids]
    return calculate_quote(c["daily_rate"], req.start_date, req.end_date, extras)



@router.post("", response_model=Booking)
def create_booking(req: BookingCreate, user: dict = Depends(current_user)):
    store = get_store()
    validate_dates(req.start_date, req.end_date)
    c = find_car(req.car_id)
    if c["status"] != "available":
        raise ApiError(409, "This car is not available for booking")
    if not user.get("licence_number") or not user.get("licence_expiry"):
        raise ApiError(422, "Add your driver's licence before booking")
    if user["licence_expiry"] < req.end_date:
        raise ApiError(422, "your licence expires before the end of this rental")
    active_count = sum(
        1 for b in store["bookings"]
        if b["user_id"] == user["id"] and b["status"] in BLOCKING_STATUSES
    )
    if active_count >= 2:
        raise ApiError(409, "You already have 2 active bookings")
    if not car_is_free(c["id"], req.start_date, req.end_date):
        raise ApiError(409, "Car is already booked for those dates")

    extras = [e for e in store["extras"] if e["id"] in req.extras_ids]
    q = calculate_quote(c["daily_rate"], req.start_date, req.end_date, extras)
    store["seq"] += 1
    from datetime import datetime, timezone
    b = {
        "id": max([0] + [x["id"] for x in store["bookings"]]) + 1,
        "reference": f"LSD-{store['seq']}",
        "user_id": user["id"], "car_id": c["id"],
        "start_date": req.start_date, "end_date": req.end_date,
        "actual_rturn_date": None, "pickup_location": req.pickup_location,
        "daily_rate_snapshot": c["daily_rate"], "days": q["days"],
        "subtotal": q["subtotal"], "extras_total": q["extras_total"],
        "extras": extras, "tax": q["tax"], "total_amount": q["total_amount"], 
        "deposit": q["deposit"], "status": "pending",
        "pickup_mileage": None, "return_mileage": None,
        "cancelled_at": None, "created_at": datetime.now(timezone.utc).isoformat(),
    }
    store["bookings"].append(b)
    return hydrate_booking(b)



@router.get("/mine", response_model=list[Booking])
def my_bookings(user: dict = Depends(current_user)):
    store = get_store()
    mine = [b for b in store["bookings"] if b["user_id"] == user["id"]]
    mine.sort(key=lambda b: b["id"], reverse=True)
    return [hydrate_booking(b) for b in mine]


@router.get("/{booking_id}", response_model=Booking)
def get_booking(booking_id: int, user: dict = Depends(current_user)):
    b = find_booking(booking_id)
    if user["role"] != "admin" and b["user_id"] != user["id"]:
        raise ApiError(403, "Not your booking")
    return hydrate_booking(b)


@router.post("/{booking_id}/cance", response_model=Booking)
def cancel_booking(booking_id: int , user: dict = Depends(current_user)):
    b = find_booking(booking_id)
    if user["role"] != "admin" and b["user_id"] != user["id"]:
        raise ApiError(403, "Not your booking")
    if b["status"] not in ("pending", "confirmed"):
        raise ApiError(409, f"cannot cancel a {b['status']} booking")
    if today_iso() >= b["start_date"]:
        raise ApiError(409, "Bookings can only be cancelled before the start date")
    b["status"] = "cancelled"
    from datetime import datetime, timezone
    b["cancelled_at"] = datetime.now(timezone.utc).sioformat()
    return hydrate_booking(b)