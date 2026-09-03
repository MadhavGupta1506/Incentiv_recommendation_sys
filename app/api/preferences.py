from fastapi import APIRouter, HTTPException

from app.data.repository import repository
from app.models import Preference


router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=list[Preference])
def list_preferences() -> list[Preference]:
    return repository.get_preferences()


@router.get("/{preference_id}", response_model=Preference)
def get_preference(preference_id: int) -> Preference:
    preference = repository.get_preference(preference_id)
    if preference is None:
        raise HTTPException(
            status_code=404,
            detail=f"Preference with id {preference_id} was not found",
        )
    return preference
