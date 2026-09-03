from fastapi import APIRouter, HTTPException

from app.data.repository import repository
from app.models import Demand


router = APIRouter(prefix="/demands", tags=["demands"])


@router.get("", response_model=list[Demand])
def list_demands() -> list[Demand]:
    return repository.get_demands()


@router.get("/{demand_id}", response_model=Demand)
def get_demand(demand_id: int) -> Demand:
    demand = repository.get_demand(demand_id)
    if demand is None:
        raise HTTPException(
            status_code=404,
            detail=f"Demand with id {demand_id} was not found",
        )
    return demand
