from dataclasses import dataclass, field
from math import exp

from app.recommendation.candidate_generation import Candidate, CandidateGenerator
from app.recommendation.features import FeatureEngineer


@dataclass(frozen=True)
class BaselineWeights:
    sector_match: float = 25.0
    valuation_match: float = 20.0
    stage_match: float = 15.0
    geography_match: float = 15.0
    historical_interest: float = 15.0
    popularity: float = 10.0

    def __post_init__(self) -> None:
        if any(weight < 0 for weight in self.as_dict().values()):
            raise ValueError("Baseline weights cannot be negative")
        if sum(self.as_dict().values()) <= 0:
            raise ValueError("At least one baseline weight must be positive")

    def as_dict(self) -> dict[str, float]:
        return {
            "sector_match": self.sector_match,
            "valuation_match": self.valuation_match,
            "stage_match": self.stage_match,
            "geography_match": self.geography_match,
            "historical_interest": self.historical_interest,
            "popularity": self.popularity,
        }


@dataclass
class ScoreBreakdown:
    total_score: float
    dimension_scores: dict[str, float]
    reasons: list[str] = field(default_factory=list)


@dataclass
class ScoredCandidate:
    candidate: Candidate
    features: dict[str, float]
    breakdown: ScoreBreakdown


class BaselineRanker:
    """Rank generated candidates with a configurable, explainable baseline."""

    def __init__(
        self,
        candidate_generator: CandidateGenerator | None = None,
        feature_engineer: FeatureEngineer | None = None,
        weights: BaselineWeights | None = None,
    ) -> None:
        self.candidate_generator = candidate_generator or CandidateGenerator()
        self.feature_engineer = feature_engineer or FeatureEngineer()
        self.weights = weights or BaselineWeights()

    def rank(self, user_id: int, limit: int = 10) -> list[ScoredCandidate]:
        candidates = self.candidate_generator.generate(user_id, limit=max(limit, 50))
        ranked = [
            self.score_candidate(
                candidate,
                self.feature_engineer.build_candidate_features(user_id, candidate),
            )
            for candidate in candidates
        ]
        ranked.sort(
            key=lambda item: (-item.breakdown.total_score, item.candidate.company.company_id)
        )
        return ranked[: max(0, limit)]

    def score_candidate(
        self,
        candidate: Candidate,
        features: dict[str, float],
    ) -> ScoredCandidate:
        normalized_history = 1.0 - exp(-features["historical_interest"] / 3.0)
        values = {
            "sector_match": features["sector_match"],
            "valuation_match": features["valuation_match"],
            "stage_match": features["stage_match"],
            "geography_match": features["geography_match"],
            "historical_interest": normalized_history,
            "popularity": features["company_popularity_score"],
        }
        weights = self.weights.as_dict()
        dimension_scores = {
            name: round(values[name] * weights[name], 4) for name in values
        }
        total_score = round(sum(dimension_scores.values()), 4)
        reasons = self._build_reasons(values)
        return ScoredCandidate(
            candidate=candidate,
            features=features,
            breakdown=ScoreBreakdown(
                total_score=total_score,
                dimension_scores=dimension_scores,
                reasons=reasons,
            ),
        )

    def rank_training_rows(self, training_data: object) -> list[float]:
        """Score point-in-time feature rows for offline baseline comparison."""
        features = training_data.features
        weights = self.weights.as_dict()
        history = 1.0 - (1.0 / (1.0 + features["historical_interest"] / 3.0))
        return (
            features["sector_match"] * weights["sector_match"]
            + features["valuation_match"] * weights["valuation_match"]
            + features["stage_match"] * weights["stage_match"]
            + features["geography_match"] * weights["geography_match"]
            + history * weights["historical_interest"]
            + features["company_popularity_score"] * weights["popularity"]
        ).tolist()

    @staticmethod
    def _build_reasons(values: dict[str, float]) -> list[str]:
        reason_by_feature = {
            "sector_match": "Matches a preferred sector",
            "valuation_match": "Fits the preferred valuation range",
            "stage_match": "Matches a preferred company stage",
            "geography_match": "Matches a preferred geography",
            "historical_interest": "Builds on previous user interest",
            "popularity": "Has strong overall engagement",
        }
        return [
            reason_by_feature[name]
            for name, value in values.items()
            if value > 0
        ]
