from app.recommendation.candidate_generation import CandidateGenerator


def test_generates_deduplicated_active_candidates_from_all_sources() -> None:
    candidates = CandidateGenerator().generate(user_id=1, limit=200)

    company_ids = [candidate.company.company_id for candidate in candidates]
    sources = {source for candidate in candidates for source in candidate.sources}

    assert len(company_ids) == len(set(company_ids))
    assert all(candidate.company.status == "active" for candidate in candidates)
    assert {"preference", "historical", "popular", "similar"}.issubset(sources)


def test_historical_interest_is_weighted_by_event_strength() -> None:
    candidates = CandidateGenerator().generate(user_id=1, limit=200)
    historical = [
        candidate for candidate in candidates if "historical" in candidate.sources
    ]

    assert historical
    assert max(candidate.historical_interest for candidate in historical) >= 1.0


def test_unknown_user_uses_popular_fallback() -> None:
    candidates = CandidateGenerator().generate(user_id=999999, limit=10)

    assert len(candidates) == 10
    assert all("popular" in candidate.sources for candidate in candidates)


def test_limit_and_order_are_deterministic() -> None:
    generator = CandidateGenerator()

    first = generator.generate(user_id=1, limit=7)
    second = generator.generate(user_id=1, limit=7)

    assert [candidate.company.company_id for candidate in first] == [
        candidate.company.company_id for candidate in second
    ]
    assert len(first) == 7
