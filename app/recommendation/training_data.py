from collections import defaultdict
from dataclasses import dataclass

import pandas as pd

from app.data.repository import DataRepository, repository
from app.models import Interaction
from app.recommendation.ml_ranking import InteractionLabels
from app.recommendation.features import HORIZON_ENCODING, RISK_ENCODING


@dataclass
class RankingTrainingData:
    features: pd.DataFrame
    labels: list[int]
    groups: list[int]
    user_ids: list[int]
    company_ids: list[int]
    timestamps: list[str]


class TrainingDataBuilder:
    """Create point-in-time ranking rows from historical interactions."""

    def __init__(
        self,
        data_repository: DataRepository = repository,
        labels: InteractionLabels | None = None,
    ) -> None:
        self.repository = data_repository
        self.labels = labels or InteractionLabels()

    def build(self) -> RankingTrainingData:
        interactions = sorted(
            self.repository.interactions,
            key=lambda item: (item.timestamp, item.interaction_id),
        )
        prior_events: defaultdict[int, list[Interaction]] = defaultdict(list)
        rows: list[dict[str, float]] = []
        labels: list[int] = []
        user_ids: list[int] = []
        company_ids: list[int] = []
        timestamps: list[str] = []

        for interaction in interactions:
            company = self.repository.get_company(interaction.company_id)
            preference = self.repository.get_preference_for_user(interaction.user_id)
            if company is None:
                continue

            history = [
                event
                for event in prior_events[interaction.user_id]
                if event.timestamp < interaction.timestamp
            ]
            rows.append(self._build_features(interaction, company, preference, history))
            labels.append(self.labels.label_for(interaction.event_type))
            user_ids.append(interaction.user_id)
            company_ids.append(interaction.company_id)
            timestamps.append(interaction.timestamp.isoformat())
            prior_events[interaction.user_id].append(interaction)

        frame = pd.DataFrame(rows)
        ordered_users = pd.Series(user_ids)
        groups = ordered_users.value_counts(sort=False).sort_index().tolist()
        order = ordered_users.argsort(kind="stable").tolist()
        frame = frame.iloc[order].reset_index(drop=True)
        labels = [labels[index] for index in order]
        user_ids = [user_ids[index] for index in order]
        company_ids = [company_ids[index] for index in order]
        timestamps = [timestamps[index] for index in order]
        return RankingTrainingData(frame, labels, groups, user_ids, company_ids, timestamps)

    @staticmethod
    def _build_features(interaction, company, preference, history) -> dict[str, float]:
        event_counts = {
            event_type: sum(event.event_type == event_type for event in history)
            for event_type in ("impression", "view", "click", "save", "shortlist", "contact")
        }
        interest = sum(
            {"impression": 0.05, "view": 0.2, "click": 0.4, "save": 0.6, "shortlist": 0.8, "contact": 1.0}[event.event_type]
            for event in history
            if event.company_id == interaction.company_id
        )
        features: dict[str, float] = {
            "historical_interaction_count": float(len(history)),
            **{f"historical_{event_type}_count": float(count) for event_type, count in event_counts.items()},
            "company_valuation": company.valuation,
            "company_quality_score": company.quality_score,
            "company_popularity_score": company.popularity_score,
            "company_is_active": float(company.status == "active"),
            "historical_interest": interest,
            "similar_company_score": 0.0,
            "preference_source": 0.0,
            "historical_source": float(interest > 0),
            "popular_source": 0.0,
        }
        if preference is None:
            return {
                **features,
                "sector_match": 0.0,
                "stage_match": 0.0,
                "geography_match": 0.0,
            }

        features.update(
            {
                "preferred_sector_count": float(len(preference.preferred_sectors)),
                "preferred_stage_count": float(len(preference.preferred_stages)),
                "preferred_geography_count": float(len(preference.preferred_geographies)),
                "preferred_deal_type_count": float(len(preference.preferred_deal_types)),
                "investment_min": preference.investment_min,
                "investment_max": preference.investment_max,
                "valuation_min": preference.valuation_min,
                "valuation_max": preference.valuation_max,
                "min_expected_return_pct": preference.min_expected_return_pct,
                "risk_appetite": RISK_ENCODING[preference.risk_appetite],
                "investment_horizon": HORIZON_ENCODING[preference.investment_horizon],
                "company_age_min_years": float(preference.company_age_min_years),
                "company_age_max_years": float(preference.company_age_max_years),
                "esg_preference": float(preference.esg_preference),
                "sector_match": float(company.sector in preference.preferred_sectors),
                "stage_match": float(company.stage in preference.preferred_stages),
                "geography_match": float(company.geography in preference.preferred_geographies),
                "valuation_match": float(preference.valuation_min <= company.valuation <= preference.valuation_max),
            }
        )
        return features
