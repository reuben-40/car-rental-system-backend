from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ..deps import current_user
from ..errors import ApiError
from ..schemas import TokenResponse, User, UserUpdate
from ..store import get_store


router = APIRouter(prefix="/auth", tags=["auth"])



def _public_user(u: dict) -> dict:
    return {
        "id": u["id"], "full_name": u["full_name"], "email": u["email"],
        "phone": u["phone"], "role": u["role"], 
        "licence_number": u.get("licence_number"),
        "licence_expiry": u.get("licence_expiry"),
        "is_active": u["is_active"], "created_at": u["created_at"],
    }


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    store = get_store()
    user = next((u for u in store["users"] if u["email"].lower() == form.username.lower()), None)
    if not user or not verify_password(form.password, user["password_hash"]):
        raise ApiError(401, "Incorrect Email or password")
    if not user["is_active"]:
        raise ApiError(403, "Account is disabled")
    token = create_access_token(user["id"])
    return {"access_token": token, "token_type": "bearer", "user": _public_user(user)}


@router.get("/me", response_model=User)
def me(user: dict = Depends(current_user)):
    return _public_user(user)


@router.patch("/me", response_model=user)
def update_me(data: UserUpdate, User: dict = Depends(current_user)):
    store = get_store()
    u = next(x for x in store["users"] if x ["id"] == user["id"])
    updates = data.model_dump(exclude_unset=True)
    for k, v in updates.items():
        u[k] = v
        return _public_user(u)