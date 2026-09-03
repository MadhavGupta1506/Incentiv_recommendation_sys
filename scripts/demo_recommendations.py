import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.recommendation.evaluation import compare_rankings
from app.recommendation.ml_ranking import LightGBMRanker
from app.recommendation.ranking import BaselineRanker
from app.recommendation.recommender import RecommendationEngine
from app.recommendation.training_data import TrainingDataBuilder


def main() -> None:
    training_data = TrainingDataBuilder().build()
    ml_ranker = LightGBMRanker().train(
        training_data.features,
        training_data.labels,
        training_data.groups,
    )
    model_path = Path("model/ranker.txt")
    ml_ranker.save(model_path)

    baseline_scores = BaselineRanker().rank_training_rows(training_data)
    ml_scores = ml_ranker.predict(training_data.features)
    comparison = compare_rankings(
        training_data.labels,
        baseline_scores,
        ml_scores,
        training_data.groups,
    )

    engine = RecommendationEngine(ml_ranker=ml_ranker)
    print("Baseline metrics:", comparison.baseline.as_dict())
    print("ML metrics:", comparison.ml.as_dict())
    for recommendation in engine.get_recommendations(1, limit=10, model="ml"):
        print(recommendation.as_dict())


if __name__ == "__main__":
    main()
