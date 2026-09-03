from collections import Counter

from app.recommendation.ml_ranking import MLScoredCandidate
from app.recommendation.ranking import ScoredCandidate


class BusinessReranker:
    """Apply deterministic business constraints after model scoring."""

    def __init__(self, max_per_sector: int = 2) -> None:
        if max_per_sector < 1:
            raise ValueError("max_per_sector must be positive")
        self.max_per_sector = max_per_sector

    def apply(
        self,
        ranked: list[ScoredCandidate] | list[MLScoredCandidate],
        limit: int,
    ) -> list[ScoredCandidate] | list[MLScoredCandidate]:
        selected = []
        sector_counts: Counter[str] = Counter()
        for result in ranked:
            company = result.candidate.company
            if company.status != "active":
                continue
            if sector_counts[company.sector] >= self.max_per_sector:
                continue
            selected.append(result)
            sector_counts[company.sector] += 1
            if len(selected) == limit:
                break
        return selected
