"""pricing & availability rules - mirror src/lib/pricing.ts exactly"""

from __future__ import annotations
from datetime import date, timedelta


TAX_RATE = 0.16
DEPOSIT_RATE = 0.2
BLOCKING_STATUSES = {"pending", "confirmed", "active"}


def _parse(iso: str) -> date:
    y, m, d = iso.split("-")
    return date(int(y), int(m), int(d))


def days_between(start: str, end:str) -> int:
    """whole days between start and end (end exclusive)."""
    return (_parse(end) - _parse(start)).days


def overlaps(a_start: str, a_end: str, b_start: str, b_end: str) -> bool:
    """overlap rule: a_start < b_end AND a_end > b_start."""
    return a_start < b_end and a_end > b_start


def today_iso() -> str:
    return date.today().isoformat()


def add_days(iso: str, n: int) -> str:
    return (_parse(iso) + timedelta(days=n)).isoformat()


def _cents(n: float) -> int:
    return round(n * 100)


def _kes(c: int) -> float:
    return c / 100


def calculate_quote(daily_rate: float, start: str, end: str, extras: list) -> dict:
    """return a Quote dict matching the frontend calculateQuote()."""
    days = days_between(start, end)
    subtotal_c = _cents(daily_rate) * days
    extras_c = 0
    for e in extras:
        price = e["price"] if isinstance(e, dict) else e.price
        per_day = e["per_day"] if isinstance(e, dict) else e.per_day
        extras_c += _cents(price) * (days if per_day else 1)
    taxable_c = subtotal_c + extras_c
    tax_c = round(taxable_c * TAX_RATE)
    total_c = taxable_c + tax_c
    deposit_c = round(total_c * DEPOSIT_RATE)
    return {
        "days": days,
        "daily_rate": daily_rate,
        "subtotal": _kes(subtotal_c),
        "extras_total": _kes(extras_c),
        "tax": _kes(tax_c),
        "total_amount": _kes(total_c),
        "deposit": _kes(deposit_c),
    }



def validate_dates(start: str, end: str) -> None:
    from .errors import ApiError
    if not start or not end:
        raise ApiError(422, "Start and end dates are required")
    if end <= start:
        raise ApiError(422, "End date must be after start date")
    today = today_iso()
    if start < today:
        raise ApiError(422, "start date cannot be in the past")
    if start > add_days(today, 365):
        raise ApiError(422, "Bookings can start at most 12 ahead")