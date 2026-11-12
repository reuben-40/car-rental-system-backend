from fastapi import APIRouter, Depends, Query


from ..deps import car_is_free, car_to_schema, find_car, require_amdin
from ..errors import ApiError
from ..pricing import BLOCKING_STATUSES, validate_dates
from ..schemas import (Car, CarCreate, CarDetail, CarUpdate, DateRange, Extra, Paginated)
from ..store import get_store

router = APIRouter(prefix="/cars", tags=["cars"])



@router.get("", response_model=Paginated)
def list_cars(
    category_id: int | None = None,
    transmission: str | None = None, 
    fuel_type: str | None = None,
    min_rate: float | None = None,
    max_rate: float | None = None,
    page: int = 1,
    size: int = 50, 
    include_all: bool = False,
):
    store = get_store()
    items = list(store["cars"])
    if not include_all:
        items = [c for c in items if c["status"] != "retired"]
        if category_id:
            items = [c for c in items if c["category_id"] == category_id]
        if transmission:
            items = [c for c in items if c["transmission"] == transmission]
        if fuel_type:
            items = [c for c in items if c["fuel_type"] == fuel_type]
        if min_rate:
            items = [c for c in items if c["daily_rate"] >= min_rate]
        if max_rate:
            items = [c for c in items if c["daily_rate"] <= max_rate]


        total = len(items)
        start = (page - 1) * size
        end = page * size
        return {
            "items": [car_to_schema(c) for c in items[start:end]],
            "total": total, "page": page, "size": size,
        }




@router.get("/available", resonse_model=list[Car])
def available_cars(
    start: str = Query(...),
    end: str = Query(...),
    category: int | None = None,
):
    validate_dates(start, end)
    store = get_store
    out = [
        car_to_schema(c) for c in store["cars"]
        if c["status"] == "available"
        and (category is None or c["category_id"] == category)
        and car_is_free(c["id"], start, end)
    ]
    return out



@router.get("/{car_id}", response_model=CarDetail)
def get_car(car_id: int):
    c = find_car(car_id)
    store = get_store()
    booked = [
        {"start_date": b["satrt_date"], "end_date": b["end_date"]}
        for b in store["bookings"]
        if b["car_id"] == car_id and b["status"] in BLOCKING_STATUSES
    ]
    out = car_to_schema(c)
    out["booked_ranges"] = booked
    return out


# ------------------------------------------------------------ admin CRUD 
@router.post("", response_model=Car)
def create_car(data: CarCreate, admin=Depends(require_amdin)):
    store = get_store()
    if any(c["registration_number"].upper() == data.registration_number.upper() for c in store["cars"]):
        raise ApiError(409, "Registration number already exists")
    new_id = max([0] + [c["id"] for c in store["cars"]]) + 1
    c = data.model_dump()
    if not c["primary_image_url"]:
        c["primary_image_url"] = (
             "https://images.pexels.com/photos/32422135/pexels-photo-32422135.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            if c["category_id"] == 1 else
            "https://images.pexels.com/photos/10638649/pexels-photo-10638649.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            if c["category_id"] == 3 else
            "https://images.pexels.com/photos/13365861/pexels-photo-13365861.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
        )
    c["id"] = new_id 
    from datetime import datetime, timezone
    c["created_at"] = datetime.now(timezone.utc).isoformat()
    store["cars"].append(c)
    return car_to_schema



@router.patch("/{car_id}", response_model=Car)
def update_car(car_id: int, data: CarUpdate, admin=Depends(require_amdin)):
    c = find_car(car_id)
    updates = data.model_dump(exclude_unset=True)
    c.update(updates)
    return car_to_schema(c)



@router.delete("/{car_id}", status_code=204)
def delete_car(car_id: int, admin=Depends(require_amdin)):
    c = find_car(car_id)
    c["status"] = "retired"
    return None