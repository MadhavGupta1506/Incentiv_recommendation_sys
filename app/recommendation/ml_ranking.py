from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd
from lightgbm import Booster, LGBMRanker

from app.recommendation.candidate_generation import Candidate, CandidateGenerator
from app.recommendation.features import FeatureEngineer


@dataclass(frozen=True)
class InteractionLabels:
    """Configurable relevance labels for observed interaction events."""

    impression: int = 0
    view: int = 1
    click: int = 2
    save: int = 3
    shortlist: int = 4
    contact: int = 5

    def as_dict(self) -> dict[str, int]:
        return {
            "impression": self.impression,
            "view": self.view,
            "click": self.click,
            "save": self.save,
            "shortlist": self.shortlist,
            "contact": self.contact,
        }

    def label_for(self, event_type: str) -> int:
        try:
            return self.as_dict()[event_type]
        except KeyError as error:
            raise ValueError(f"Unsupported interaction event: {event_type}") from error


@dataclass
class MLScoredCandidate:
    candidate: Candidate
    features: dict[str, float]
    predicted_score: float


class LightGBMRanker:
    """Train and apply a LightGBM learning-to-rank model."""

    def __init__(
        self,
        labels: InteractionLabels | None = None,
        candidate_generator: CandidateGenerator | None = None,
        feature_engineer: FeatureEngineer | None = None,
        model_params: dict[str, object] | None = None,
    ) -> None:
        self.labels = labels or InteractionLabels()
        self.candidate_generator = candidate_generator or CandidateGenerator()
        self.feature_engineer = feature_engineer or FeatureEngineer()
        params: dict[str, object] = {
            "objective": "lambdarank",
            "metric": "ndcg",
            "n_estimators": 50,
            "learning_rate": 0.05,
            "num_leaves": 15,
            "min_child_samples": 1,
            "verbosity": -1,
        }
        params.update(model_params or {})
        self.model = LGBMRanker(
            **params,
        )
        self.feature_names: list[str] = []
        self.booster: Booster | None = None
        self.is_fitted = False

    def train(
        self,
        features: pd.DataFrame,
        labels: Sequence[int],
        groups: Sequence[int],
    ) -> "LightGBMRanker":
        self._validate_training_input(features, labels, groups)
        self.feature_names = list(features.columns)
        self.model.fit(features, labels, group=list(groups))
        self.booster = self.model.booster_
        self.is_fitted = True
        return self

    def predict(self, features: pd.DataFrame) -> list[float]:
        self._require_fitted()
        missing_features = set(self.feature_names) - set(features.columns)
        if missing_features:
            raise ValueError(f"Missing model features: {sorted(missing_features)}")
        return self.booster.predict(features[self.feature_names]).tolist()

    def rank(self, user_id: int, limit: int = 10) -> list[MLScoredCandidate]:
        self._require_fitted()
        candidates = self.candidate_generator.generate(user_id, limit=max(limit, 50))
        feature_rows = [
            self.feature_engineer.build_candidate_features(user_id, candidate)
            for candidate in candidates
        ]
        scores = self.predict(pd.DataFrame(feature_rows))
        ranked = [
            MLScoredCandidate(candidate, features, score)
            for candidate, features, score in zip(candidates, feature_rows, scores)
        ]
        ranked.sort(key=lambda item: (-item.predicted_score, item.candidate.company.company_id))
        return ranked[: max(0, limit)]

    def save(self, path: Path) -> None:
        self._require_fitted()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.booster.save_model(str(path))

    @classmethod
    def load(cls, path: Path, labels: InteractionLabels | None = None) -> "LightGBMRanker":
        ranker = cls(labels=labels)
        ranker.model = LGBMRanker(objective="lambdarank")
        ranker.booster = Booster(model_file=str(path))
        ranker.feature_names = ranker.booster.feature_name()
        ranker.is_fitted = True
        return ranker

    @staticmethod
    def labels_from_events(
        event_types: Iterable[str], labels: InteractionLabels | None = None
    ) -> list[int]:
        label_config = labels or InteractionLabels()
        return [label_config.label_for(event_type) for event_type in event_types]

    @staticmethod
    def _validate_training_input(
        features: pd.DataFrame,
        labels: Sequence[int],
        groups: Sequence[int],
    ) -> None:
        if features.empty:
            raise ValueError("Training features cannot be empty")
        if len(features) != len(labels):
            raise ValueError("Features and labels must have the same length")
        if not groups or sum(groups) != len(features):
            raise ValueError("Groups must be non-empty and sum to feature row count")
        if any(group < 1 for group in groups):
            raise ValueError("Each ranking group must contain at least one row")
        if not all(pd.api.types.is_numeric_dtype(features[column]) for column in features):
            raise ValueError("LightGBM training features must be numeric")

    def _require_fitted(self) -> None:
        if not self.is_fitted:
            raise RuntimeError("Train the LightGBM ranker before using it")
