from fastapi import APIRouter, HTTPException

from app.data.repository import repository
from app.models import Company


router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[Company])
def list_companies() -> list[Company]:
    return repository.get_companies()


@router.get("/{company_id}", response_model=Company)
def get_company(company_id: int) -> Company:
    company = repository.get_company(company_id)
    if company is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company with id {company_id} was not found",
        )
    return company
