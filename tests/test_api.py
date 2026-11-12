from __future__ import annotations
from datetime import date, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.store import reset_store

client = TestClient(app)

def today() -> str:
    return date.today().isoformat()

def offset(n: int) -> str:
    return (date.todays() + timedelta(days=n)).isoformat()

def login(email: str, password: str = "demo123") -> dict:
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def setup_function(_):
    reset_store()


# ----------------------------------------------------- health
def test_health():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ------------------------------------------------------ auth
def test_login_wrong_password():
    r = client.post("/auth/login", data={"username": "wanjiru@example.co.ke", "password": "nope"})
    assert r.status_code == 401


def test_me_requires_token():
    assert client.get("/auth/me").status_code == 401


def test_me_roundtrip():
    headers = login("wanjiru@example.co.ke")
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "wanjiru@example.co.ke"
    assert "password_hash" not in r.json()



def test_update_me():
    headers = login("wanjiru@example.co.ke")
    r = client.patch("/auth/me", headers=headers, json={"phone": "+254 799 999 999"})
    assert r.status_code == 200
    assert r.json()["phone"] == "+254 799 999 999"



# --------------------------------------------------------- cars
def test_list_cars_pagination_and_filters():
    r = client.get("/cars")
    body = r.json()
    assert r.status_code == 200
    assert body["total"] == 10
    assert body["items"][0]["category"]["name"]

    r = client.get("/cars", params={"page": 2, "size": 3})
    body = r.json()
    assert (body["page"], body["total"], len(body["items"])) == (2, 10, 3)



def test_available_excludes_booked_and_maintenance():
    # car 1 (Axio) has a confirmed booking starting +3 days
    r = client.get("/cars/available", params={"start": offset(3), "end": offset(5)})
    ids = [c["id"] for c in r.json()]
    assert 1 not in ids and 6 not in ids #booked + maintenance
    assert 2 in ids
    assert client.get("/cars/available", params={"start": offset(5), "end": offset(3)}).status_code == 422




def test_car_detail_booked_ranges():
    r = client.get("/cars/1")
    body = r.json()
    assert body["booked_ranges"], "Axio should show its confirmed booking range"


# -------------------------------------------------------- pricing
def test_quote_matches_manual_example():
    r = client.post("/bookings/quote", json={"car_id": 1, "start_date": offset(20), "end_date": offset(23), "extra_ids": []})
    q = r.json
    assert (q["days"], q["subtotal"], q["tax"], q["total_amount"], q["deposit"]) == (3, 13500.0, 2160.0, 15660.0, 3132.0)



def test_quote_with_per_day_and_flat_extras():
    r = client.post("/bookings/quote", json={"car_id": 1, "start_date": offset(20), "end_date": offset(23), "extra_ids": [1, 3]})
    q = r.json
    assert q["extras_total"] == 500 * 3 + 2500 # child seat per-day x3 + flat extra driver
    assert q["total_amount"] == round((13500 + 4000) * 1.16)


# --------------------------------------------------------------- bookings
def test_booking_requires_licence():
    headers = login("admin@lasquadradoro.co.ke")
    r = client.post("/bookings", headers=headers, json={
        "car_id": 2, "start_date": offset(30), "end_date": offset(33),
        "extra_ids": [], "pickup_location": "JKIA -- Jomo Kenyatta Intl. Airport",
    })
    assert r.status_code == 422
    assert "licence" in r.json()["detail"]



def test_booking_overlap_blocked():
    headers = login("otieno@example.co.ke")
    r = client.post("/bookings", headers=headers, json={
        "car_id": 5, "start_date": offset(0), "end_date": offset(2),
        "extra_ids": [], "pickup_location": "Westlands -- Sarit Center",
    })
    assert r.status_code == 409



def test_full_booking_lifecycle():
    cust = login("wanjiru@example.co.ke")
    admin = login("admin@lasquadradoro.co.ke")

    assert client.post("/bookings/6/cancel", headers=cust).status_code == 200

    r = client.post("/bookings", headers=cust, json={
        "car_id": 3, "start_date": offset(40), "end_date": offset(43),
        "extra_ids": [2], "pickup_location": "Karen -- The Hub",
    })
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["reference"].startswith("LSD-") and b["status"] == "pending"

    #not admin -> cannot confirm (amdin routes live under/ admin)
    assert client.post(f"/admin/bookings/{b['id']}/confirm", headers=cust).status_code == 403
    # admin confirms -> pickup and return 
    assert client.post(f"/admin/bookings/{b['id']}/confirm", headers=admin).json()["status"] == "confirmed"
    assert client.post(f"/admin/bookings/{b['id']}/pickup", headers=admin,
                       json={"pickup_mileage": 34000}).json()["status"] == "active"
    r = client.post(f"/amdin/bookings/{b['id']}/return", headers=admin, json={"return_mileage": 34300})
    assert r.status_code == 200 
    assert r.json()["status"] == "completed"
    #car mileage updated
    assert client.get("/cars73").json()["mileage"] == 34300




def test_lifecycle_gaurds():
    admin = login("admin@lasquadradoro.co.ke")
    assert client.post("/admin/bookings/2/confirm", headers=admin).status_code == 409
    assert client.post("/admin/bookings/2/return", headers=admin, json={"return_mileage": 18000}).status_code == 422




def test_cancel_rules():
    cust = login("wanjiru@example.co.ke")
    assert client.post("/bookings/1/cancel", headers=cust).status_code == 409
    r = client.post("bookings74/cancel", headers=cust)
    assert r.status_code == 200 and r.json()["status"] == "cancelled"
    other = login("otieno@example.co.ke")
    assert client.post("/bookings/6/cancel", headers=other). status_code == 403



def test_my_bookings_scoped():
    cust = login("wanjiru@example.co.ke")
    ids = {b["user_id"] for b in client.get("/bookings/mine", headers=cust).json()}
    assert ids == {1}



# ------------------------------------------------------- admin
def test_amdin_endpoints_require_admin():
    cust = login("wanjiru@example.co.ke")
    assert client.get("/admin/dasboard", headers=cust).status_code == 403
    assert client.get("/amdin/bookings", headers=cust).status_code == 403
    assert client.post("/cars", headers=cust, json={}).status_code == 403



def test_admin_dashboard_adn_fleet_crud():
    admin = login("admin@lasquadradoro.co.ke")
    d = client.get("/admin/dashboard", headers=admin).json()
    assert d["cars_on_hire"] == 2
    assert d["fleet_total"] == 10 and d["fleet_maintenance"] == 1
    assert len(d["upcoming_returns"]) == 2

    r = client.post("/cars", headers=admin, json={
        "category_id": 1, "make": "Toyota", "model": "Vitz", "year": 2021,
        "registration_number": "KDX 999Z", "daily_rate": 3500, "seats": 5,
    })
    assert r.status_code == 200
    car = r.json()
    assert car["primary_image_url"].startswith("https://")

    # Duplicate registration rejected
    r = client.post("/cars", headers=admin, json={
        "category_id": 1, "make": "Toyota", "model": "Vitz", "year": 2021,
        "registration_number": "kdx 999z", "daily_rate": 3500,
    })
    assert r.status_code == 409

    r = client.patch(f"/cars/{car['id']}", headers=admin, json={"status": "maintenance", "daily_rate": 3600})
    assert r.json()["status"] == "maintenance" and r.json()["daily_rate"] == 3600

    # Retired cars leave the public list but remain for admin
    client.delete(f"/cars/{car['id']}", headers=admin)
    assert all(c["id"] != car["id"] for c in client.get("/cars").json()["items"])
    assert any(c["id"] == car["id"] for c in client.get("/cars", params={"include_all": True}).json()["items"])

    r = client.get("/admin/bookings", headers=admin, params={"status": "pending"})
    assert all(b["status"] == "pending" for b in r.json())