from fastapi import APIRouter, HTTPException, Query
from pathlib import Path

from app.recommendation.recommender import RecommendationEngine
from app.recommendation.evaluation import compare_rankings
from app.recommendation.ml_ranking import LightGBMRanker
from app.recommendation.recommender import RecommendationEngine
from app.recommendation.training_data import TrainingDataBuilder



router = APIRouter(prefix="/recommendations", tags=["recommendations"])

training_data = TrainingDataBuilder().build()
ml_ranker = LightGBMRanker().train(
        training_data.features,
        training_data.labels,
        training_data.groups,
    )
model_path = Path("model/ranker.txt")
ml_ranker.save(model_path)
engine = RecommendationEngine(ml_ranker=ml_ranker)


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
