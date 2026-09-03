from app.recommendation.candidate_generation import CandidateGenerator
from app.recommendation.features import FeatureEngineer


def test_builds_user_features_from_updated_preferences_and_history() -> None:
    features = FeatureEngineer().build_user_features(1)

    assert features["preferred_sector_count"] == 2.0
    assert features["preferred_stage_count"] == 2.0
    assert features["preferred_geography_count"] == 1.0
    assert features["investment_min"] > 0
    assert features["risk_appetite"] == 1.0
    assert features["historical_interaction_count"] > 0


def test_builds_company_features() -> None:
    candidate = CandidateGenerator().generate(user_id=1, limit=1)[0]
    features = FeatureEngineer().build_company_features(candidate.company)

    assert features["company_valuation"] == candidate.company.valuation
    assert 0.0 <= features["company_quality_score"] <= 1.0
    assert 0.0 <= features["company_popularity_score"] <= 1.0


def test_builds_relationship_features_for_candidate() -> None:
    candidate = CandidateGenerator().generate(user_id=1, limit=1)[0]
    features = FeatureEngineer().build_relationship_features(1, candidate)

    assert set(
        (
            "sector_match",
            "stage_match",
            "geography_match",
            "valuation_match",
            "historical_interest",
            "similar_company_score",
        )
    ).issubset(features)
    assert all(features[name] in (0.0, 1.0) for name in ("sector_match", "stage_match", "geography_match", "valuation_match"))


def test_feature_matrix_has_one_row_per_candidate() -> None:
    generator = CandidateGenerator()
    candidates = generator.generate(user_id=1, limit=5)
    matrix = FeatureEngineer().build_feature_matrix(1, candidates)

    assert len(matrix) == len(candidates)
    assert all("company_popularity_score" in row for row in matrix)
