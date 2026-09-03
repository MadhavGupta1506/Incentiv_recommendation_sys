from app.data.repository import DataRepository, repository
from app.models import Company
from app.recommendation.candidate_generation import Candidate


RISK_ENCODING = {"Low": 0.0, "Medium": 0.5, "High": 1.0}
HORIZON_ENCODING = {"<2 years": 0.0, "2-5 years": 0.33, "5-8 years": 0.66, "8+ years": 1.0}


class FeatureEngineer:
    """Build numeric features without applying ranking or business weights."""

    def __init__(self, data_repository: DataRepository = repository) -> None:
        self.repository = data_repository

    def build_user_features(self, user_id: int) -> dict[str, float]:
        preference = self.repository.get_preference_for_user(user_id)
        interactions = self.repository.get_interactions_for_user(user_id)
        event_counts = {
            event_type: sum(interaction.event_type == event_type for interaction in interactions)
            for event_type in ("impression", "view", "click", "save", "shortlist", "contact")
        }

        features: dict[str, float] = {
            "historical_interaction_count": float(len(interactions)),
            **{f"historical_{event_type}_count": float(count) for event_type, count in event_counts.items()},
        }
        if preference is None:
            return features

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
            }
        )
        return features

    @staticmethod
    def build_company_features(company: Company) -> dict[str, float]:
        return {
            "company_valuation": company.valuation,
            "company_quality_score": company.quality_score,
            "company_popularity_score": company.popularity_score,
            "company_is_active": float(company.status == "active"),
        }

    def build_relationship_features(
        self,
        user_id: int,
        candidate: Candidate,
    ) -> dict[str, float]:
        preference = self.repository.get_preference_for_user(user_id)
        company = candidate.company
        if preference is None:
            return {
                "sector_match": 0.0,
                "stage_match": 0.0,
                "geography_match": 0.0,
                "valuation_match": 0.0,
                "historical_interest": candidate.historical_interest,
                "similar_company_score": float("similar" in candidate.sources),
                "preference_source": float("preference" in candidate.sources),
                "historical_source": float("historical" in candidate.sources),
                "popular_source": float("popular" in candidate.sources),
            }

        return {
            "sector_match": float(company.sector in preference.preferred_sectors),
            "stage_match": float(company.stage in preference.preferred_stages),
            "geography_match": float(company.geography in preference.preferred_geographies),
            "valuation_match": float(
                preference.valuation_min <= company.valuation <= preference.valuation_max
            ),
            "historical_interest": candidate.historical_interest,
            "similar_company_score": float("similar" in candidate.sources),
            "preference_source": float("preference" in candidate.sources),
            "historical_source": float("historical" in candidate.sources),
            "popular_source": float("popular" in candidate.sources),
        }

    def build_candidate_features(
        self,
        user_id: int,
        candidate: Candidate,
    ) -> dict[str, float]:
        features: dict[str, float] = {}
        features.update(self.build_user_features(user_id))
        features.update(self.build_company_features(candidate.company))
        features.update(self.build_relationship_features(user_id, candidate))
        return features

    def build_feature_matrix(
        self,
        user_id: int,
        candidates: list[Candidate],
    ) -> list[dict[str, float]]:
        return [self.build_candidate_features(user_id, candidate) for candidate in candidates]
