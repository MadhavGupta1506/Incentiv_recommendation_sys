from collections import defaultdict
from dataclasses import dataclass, field

from app.data.repository import DataRepository, repository
from app.models import Company, Preference


EVENT_WEIGHTS = {
    "impression": 0.05,
    "view": 0.2,
    "click": 0.4,
    "save": 0.6,
    "shortlist": 0.8,
    "contact": 1.0,
}


@dataclass
class Candidate:
    company: Company
    sources: set[str] = field(default_factory=set)
    historical_interest: float = 0.0


class CandidateGenerator:
    """Generate a bounded, deterministic pool of active company candidates."""

    def __init__(self, data_repository: DataRepository = repository) -> None:
        self.repository = data_repository

    def generate(self, user_id: int, limit: int = 50) -> list[Candidate]:
        if limit < 1:
            return []

        candidates: dict[int, Candidate] = {}
        preference = self.repository.get_preference_for_user(user_id)
        history = self._historical_interest(user_id)

        if preference is not None:
            for company in self._preference_candidates(preference):
                self._add(candidates, company, "preference")
        for company_id, interest in history.items():
            company = self.repository.get_company(company_id)
            if company is not None and company.status == "active":
                self._add(candidates, company, "historical", interest)

        for company in self._popular_candidates():
            self._add(candidates, company, "popular")

        for company in self._similar_candidates(history):
            self._add(candidates, company, "similar")

        return sorted(
            candidates.values(),
            key=lambda candidate: (
                -int("preference" in candidate.sources),
                -candidate.historical_interest,
                -candidate.company.popularity_score,
                candidate.company.company_id,
            ),
        )[:limit]

    def _preference_candidates(self, preference: Preference) -> list[Company]:
        preferred_sectors = set(preference.preferred_sectors)
        preferred_stages = set(preference.preferred_stages)
        preferred_geographies = set(preference.preferred_geographies)

        matches = []
        for company in self.repository.get_companies():
            if company.status != "active":
                continue
            score = (
                int(company.sector in preferred_sectors),
                int(company.stage in preferred_stages),
                int(company.geography in preferred_geographies),
                int(preference.valuation_min <= company.valuation <= preference.valuation_max),
            )
            if any(score):
                matches.append((score, company))

        matches.sort(key=lambda item: (item[0], -item[1].popularity_score, -item[1].company_id), reverse=True)
        print(matches)
        return [company for _, company in matches]

    def _historical_interest(self, user_id: int) -> dict[int, float]:
        interest: defaultdict[int, float] = defaultdict(float)
        for interaction in self.repository.get_interactions_for_user(user_id):
            interest[interaction.company_id] += EVENT_WEIGHTS[interaction.event_type]
        return dict(interest)

    def _popular_candidates(self) -> list[Company]:
        return sorted(
            (company for company in self.repository.get_companies() if company.status == "active"),
            key=lambda company: (-company.popularity_score, company.company_id),
        )

    def _similar_candidates(self, history: dict[int, float]) -> list[Company]:
        historical_companies = {
            company.company_id: company
            for company in self.repository.get_companies()
            if company.company_id in history
        }
        if not historical_companies:
            return []

        scored = []
        for company in self.repository.get_companies():
            if company.status != "active" or company.company_id in historical_companies:
                continue
            similarity = max(
                self._attribute_similarity(company, historical_company)
                for historical_company in historical_companies.values()
            )
            if similarity:
                scored.append((similarity, company))

        scored.sort(key=lambda item: (-item[0], -item[1].popularity_score, item[1].company_id))
        return [company for _, company in scored]

    @staticmethod
    def _attribute_similarity(left: Company, right: Company) -> int:
        return sum(
            (
                left.sector == right.sector,
                left.stage == right.stage,
                left.geography == right.geography,
            )
        )

    @staticmethod
    def _add(
        candidates: dict[int, Candidate],
        company: Company,
        source: str,
        historical_interest: float = 0.0,
    ) -> None:
        candidate = candidates.setdefault(company.company_id, Candidate(company=company))
        candidate.sources.add(source)
        candidate.historical_interest = max(candidate.historical_interest, historical_interest)
