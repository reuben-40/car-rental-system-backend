from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import admin, auth, bookings, cars, extras
from .store import save_store

app = FastAPI(
    title="La Squadra d'Oro API",
    description="Car rental backend (Nairobi, KES),",
    version="1.0.0",
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.FRONTEND_ORIGIN == "*" else [settings.FRONTEND_ORIGIN],
    allow_credentials=settings.FRONTEND_ORIGIN !="*",
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.middleware("http")
async def persist_changes(request, call_next):
    response = await call_next(request)
    if request.method in {"POST", "PATCH", "PUT", "DELETE"}:
        save_store()
    return response

app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(extras.router)
app.include_router(bookings.router)
app.include_router(admin.router)

@app.get("/", tags=["health"])
def root():
    return {"service": "la-squdra-doro-api", "status": "ok"}