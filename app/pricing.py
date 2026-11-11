from datetime import date, datetime, timedelta
from typing import Any, Dict, List

TAX_RATE = 0.16
DEFAULT_SECURITY_DEPOSIT = 15000.0  # KES


def today_iso() -> str:
    """Returns today's date formatted as YYYY-MM-DD."""
    return date.today().isoformat()


def add_days(iso_date: str, days: int) -> str:
    """Adds a positive or negative number of days to an ISO date string."""
    dt = date.fromisoformat(iso_date)
    return (dt + timedelta(days=days)).isoformat()


def calculate_quote(
    daily_rate: float,
    start_date: str | date,
    end_date: str | date,
    selected_extras: List[Dict[str, Any]] | None = None,
    deposit: float = DEFAULT_SECURITY_DEPOSIT,
) -> Dict[str, float | int]:
    """Calculates rental days, subtotals, 16% VAT, deposit, and total KES amount."""
    d_start = date.fromisoformat(start_date) if isinstance(start_date, str) else start_date
    d_end = date.fromisoformat(end_date) if isinstance(end_date, str) else end_date

    days = max((d_end - d_start).days, 1)
    subtotal = round(float(daily_rate * days), 2)

    extras_total = 0.0
    for extra in (selected_extras or []):
        price = float(extra.get("price", 0.0))
        if extra.get("per_day", True):
            extras_total += price * days
        else:
            extras_total += price
    extras_total = round(extras_total, 2)

    taxable = subtotal + extras_total
    tax = round(taxable * TAX_RATE, 2)
    total_amount = round(taxable + tax + deposit, 2)

    return {
        "days": days,
        "subtotal": subtotal,
        "extras_total": extras_total,
        "tax": tax,
        "deposit": float(deposit),
        "total_amount": total_amount,
    }