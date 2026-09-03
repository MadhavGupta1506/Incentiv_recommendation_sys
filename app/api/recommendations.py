from fastapi import APIRouter, HTTPException, Query

from app.recommendation.recommender import RecommendationEngine


router = APIRouter(prefix="/recommendations", tags=["recommendations"])
engine = RecommendationEngine()


@router.get("/{user_id}")
def get_recommendations(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    model: str = Query(default="baseline", pattern="^(baseline|ml)$"),
) -> list[dict[str, object]]:
    try:
        recommendations = engine.get_recommendations(user_id, limit, model)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return [recommendation.as_dict() for recommendation in recommendations]
