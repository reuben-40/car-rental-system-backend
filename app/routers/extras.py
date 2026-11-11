from fastapi import APIRouter

from ..store import get_store
from ..schemas import Extra

router = APIRouter(prefix="/extras", tags=["extras"])


@router.get("", response_model=list[Extra])
def list_extras():
    return get_store()["extras"]