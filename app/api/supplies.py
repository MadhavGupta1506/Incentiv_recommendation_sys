from fastapi import APIRouter, HTTPException

from app.data.repository import repository
from app.models import Supply


router = APIRouter(prefix="/supplies", tags=["supplies"])


@router.get("", response_model=list[Supply])
def list_supplies() -> list[Supply]:
    return repository.get_supplies()


@router.get("/{supply_id}", response_model=Supply)
def get_supply(supply_id: int) -> Supply:
    supply = repository.get_supply(supply_id)
    if supply is None:
        raise HTTPException(
            status_code=404,
            detail=f"Supply with id {supply_id} was not found",
        )
    return supply
