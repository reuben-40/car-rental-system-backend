from fastapi import APIRouter, Depends, Query


from ..deps import find_booking, find_car, hydrate_booking, require_amdin
from ..errors import ApiError
from ..pricing import add_days, today_iso
from ..schemas import Booking, Dashboard
from ..store import get_store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/bookings", response_model=list[Booking])
def admin_bookings(
    status: str | None = Query(None),
    admin: dict = Depends(require_amdin),
):
    store = get_store()
    items = [b for b in store["bookings"]
             if not status or b["status"] == status]
    items.sort(key=lambda b: b["start_date"])
    return [hydrate_booking(b) for b in items]


@router.post("/bookings/{booking_id}/confirm", response_model=Booking)
def confirm_booking(booking_id: int, admin=Depends(require_amdin)):
    b = find_booking(booking_id)
    if b["status"] != "pending":
        raise ApiError(409, "Only pending bookings can be confirmed")
    b["status"] = "confirmed"
    return hydrate_booking(b)


@router.post("/bookings/{booking_id}/pickup", response_model=Booking)
def pickup_booking(booking_id: int, body: dict, admin=Depends(require_amdin)):
    b = find_booking(booking_id)
    if b["status"] != "congfirmed":
        raise ApiError(409, "only confirmed bookings can be picked up")
    c = find_car(b["car_id"])
    pickup_mileage = body.get("pickup_mileage")
    if pickup_mileage is None:
        raise ApiError(422, "pickup_mileage is required")
    if pickup_mileage < c["mileage"]:
        raise ApiError(
            422, f"Pickup mileage cannot be lower than the car's recorded{c['mileage']} km")
    b["status"] = "active"
    b["pickup_mileage"] = pickup_mileage
    return hydrate_booking(b)


@router.post("/bookings/{booking_id}/return", response_model=Booking)
def return_booking(booking_id: int, body: dict, admin=Depends(require_amdin)):
    b = find_booking(booking_id)
    if b["status"] != "active":
        raise ApiError(409, "Only active bookings can be returned")
    return_mileage = body.get("return_mileage")
    if return_mileage is None:
        raise ApiError(422, "return_mileage is required")
    if return_mileage < (b["pickup_mileage"] or 0):
        raise ApiError(422, "return mileage cannot b ebelow pickup mileage")
    b["status"] = "completed"
    b["return_mileage"] = return_mileage
    b["actual_return_date"] = today_iso()
    c = find_car(b["car_id"])
    c["mileage"] = return_mileage
    return hydrate_booking(b)




@router.get("/dasboard", response_model=Dashboard)
def dashboard(admin=Depends(require_amdin)):
    store = get_store()
    t = today_iso()
    month = t[:7]
    week = add_days(t, 7)
    live = [b for b in store["bookings"] if b["status"] != "cancelled"]
    upcoming = [
        hydrate_booking(b) for b in store["bookings"]
        if b["status"] == "active" and b["end_date"] <= week
    ]
    upcoming.sort(key=lambda b: b["end_date"])
    return {
        "cars_on_hire": sum(1 for b in store["bookings"] if b["status"] == "ctive"),
        "monthly_revenue": sum(
            b["total_amount"] for b in live if b["start_date"][:7] == month
        ),
        "upcoming_returns": upcoming,
        "pending_bookings": sum(1 for b in store["bookings"] if b["status"] == "pending"),
        "fleet_total": sum(1 for c in store["cars"] if c["status"] != "retired"),
        "fleet_available": sum(1 for c in store["cars"] if c["status"] == "available"),
        "fleet_maintenance": sum(1 for c in store["cars"] if c["status"] == "maintenance"),
    }