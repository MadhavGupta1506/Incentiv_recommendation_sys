from fastapi import APIRouter, HTTPException

from app.data.repository import repository
from app.models import Company, Demand, Preference, Supply


router = APIRouter()


@router.get("/companies", response_model=list[Company], tags=["companies"])
def list_companies() -> list[Company]:
    return repository.get_companies()


@router.get("/companies/{company_id}", response_model=Company, tags=["companies"])
def get_company(company_id: int) -> Company:
    company = repository.get_company(company_id)
    if company is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company with id {company_id} was not found",
        )
    return company


@router.get("/supplies", response_model=list[Supply], tags=["supplies"])
def list_supplies() -> list[Supply]:
    return repository.get_supplies()


@router.get("/supplies/{supply_id}", response_model=Supply, tags=["supplies"])
def get_supply(supply_id: int) -> Supply:
    supply = repository.get_supply(supply_id)
    if supply is None:
        raise HTTPException(
            status_code=404,
            detail=f"Supply with id {supply_id} was not found",
        )
    return supply


@router.get("/demands", response_model=list[Demand], tags=["demands"])
def list_demands() -> list[Demand]:
    return repository.get_demands()


@router.get("/demands/{demand_id}", response_model=Demand, tags=["demands"])
def get_demand(demand_id: int) -> Demand:
    demand = repository.get_demand(demand_id)
    if demand is None:
        raise HTTPException(
            status_code=404,
            detail=f"Demand with id {demand_id} was not found",
        )
    return demand


@router.get("/preferences", response_model=list[Preference], tags=["preferences"])
def list_preferences() -> list[Preference]:
    return repository.get_preferences()


@router.get(
    "/preferences/{preference_id}",
    response_model=Preference,
    tags=["preferences"],
)
def get_preference(preference_id: int) -> Preference:
    preference = repository.get_preference(preference_id)
    if preference is None:
        raise HTTPException(
            status_code=404,
            detail=f"Preference with id {preference_id} was not found",
        )
    return preference
