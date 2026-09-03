from dataclasses import dataclass

from app.recommendation.ml_ranking import LightGBMRanker, MLScoredCandidate
from app.recommendation.ranking import BaselineRanker, ScoredCandidate
from app.recommendation.reranking import BusinessReranker


@dataclass(frozen=True)
class Recommendation:
    company_id: int
    company_name: str
    score: float
    score_breakdown: dict[str, float]
    reasons: list[str]
    sources: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "score": self.score,
            "score_breakdown": self.score_breakdown,
            "reasons": self.reasons,
            "sources": self.sources,
        }


class RecommendationEngine:
    """Orchestrate generation, ranking, re-ranking, and explanations."""

    def __init__(
        self,
        baseline_ranker: BaselineRanker | None = None,
        ml_ranker: LightGBMRanker | None = None,
        reranker: BusinessReranker | None = None,
    ) -> None:
        self.baseline_ranker = baseline_ranker or BaselineRanker()
        self.ml_ranker = ml_ranker
        self.reranker = reranker or BusinessReranker()

    def get_recommendations(self, user_id: int, limit: int = 10, model: str = "baseline") -> list[Recommendation]:
        if limit < 1:
            return []
        if model == "baseline":
            ranked = self.baseline_ranker.rank(user_id, limit=max(limit * 3, 30))
            selected = self.reranker.apply(ranked, limit)
            return [self._from_baseline(result) for result in selected]
        if model == "ml":
            if self.ml_ranker is None:
                raise RuntimeError("An ML ranker must be supplied for model='ml'")
            ranked = self.ml_ranker.rank(user_id, limit=max(limit * 3, 30))
            selected = self.reranker.apply(ranked, limit)
            return [self._from_ml(result) for result in selected]
        raise ValueError("model must be 'baseline' or 'ml'")

    @staticmethod
    def _from_baseline(result: ScoredCandidate) -> Recommendation:
        return Recommendation(
            company_id=result.candidate.company.company_id,
            company_name=result.candidate.company.name,
            score=result.breakdown.total_score,
            score_breakdown=result.breakdown.dimension_scores,
            reasons=result.breakdown.reasons,
            sources=sorted(result.candidate.sources),
        )

    @staticmethod
    def _from_ml(result: MLScoredCandidate) -> Recommendation:
        return Recommendation(
            company_id=result.candidate.company.company_id,
            company_name=result.candidate.company.name,
            score=round(result.predicted_score, 6),
            score_breakdown={},
            reasons=["Ranked by the trained LightGBM model"],
            sources=sorted(result.candidate.sources),
        )
