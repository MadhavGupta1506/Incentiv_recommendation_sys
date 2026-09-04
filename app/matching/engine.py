from dataclasses import dataclass

from app.data.repository import DataRepository, repository
from app.models import Company, Demand, Preference, Supply


@dataclass(frozen=True)
class MatchScore:
    total_score: float
    company_sector_alignment: float
    valuation_fit: float
    deal_size_fit: float
    stage_fit: float
    price_reasonableness: float
    reasons: list[str]


@dataclass(frozen=True)
class SupplyDemandMatch:
    supply: Supply
    demand: Demand
    supply_company: Company
    demand_company: Company
    score: MatchScore


class MatchingEngine:
    """Rank counterparties against only the requesting user's preferences."""

    def __init__(self, data_repository: DataRepository = repository) -> None:
        self.repository = data_repository

    def match_supply(self, supply_id: int, limit: int = 10) -> list[SupplyDemandMatch]:
        supply = self.repository.get_supply(supply_id)
        if supply is None:
            raise LookupError(f"Supply with id {supply_id} was not found")
        
        # If no company found raise this error
        company = self._company_or_error(supply.company_id)
        
        # If no preference found raise this
        preference = self._preference_or_error(supply.created_by)
        candidates = [
            demand
            for demand in self.repository.get_demands()
            if demand.status == "active"
            and demand.currency.upper() == supply.currency.upper()
        ]
        return self._rank(supply, company, preference, candidates, limit)

    def match_demand(self, demand_id: int, limit: int = 10) -> list[SupplyDemandMatch]:
        demand = self.repository.get_demand(demand_id)
        if demand is None:
            raise LookupError(f"Demand with id {demand_id} was not found")
        company = self._company_or_error(demand.company_id)
        preference = self._preference_or_error(demand.created_by)
        candidates = [
            supply
            for supply in self.repository.get_supplies()
            if supply.status == "active"
            and supply.currency.upper() == demand.currency.upper()
        ]
        return self._rank(demand, company, preference, candidates, limit)

    def _rank(self, request, request_company, preference, candidates, limit):
        matches = []
        for candidate in candidates:
            candidate_company = self._company_or_error(candidate.company_id)
            
            score = self._score(
                request,
                request_company,
                candidate,
                candidate_company,
                preference,
            )
            
            matches.append(
                SupplyDemandMatch(
                    supply=request if isinstance(request, Supply) else candidate,
                    demand=candidate if isinstance(request, Supply) else request,
                    supply_company=request_company if isinstance(request, Supply) else candidate_company,
                    demand_company=candidate_company if isinstance(request, Supply) else request_company,
                    score=score,
                )
            )
            
        matches.sort(key=lambda match: (-match.score.total_score, match.demand.demand_id, match.supply.supply_id))
        return matches[: max(0, limit)]

    @staticmethod
    def _score(request, request_company, candidate, candidate_company, preference: Preference) -> MatchScore:
        candidate_amount = (
            candidate.investment_amount_min + candidate.investment_amount_max
        ) / 2 if isinstance(candidate, Demand) else candidate.units_to_sell * candidate.expected_price_per_unit
        
        # request_amount = (
        #     request.units_to_sell * request.expected_price_per_unit
        #     if isinstance(request, Supply)
        #     else (request.investment_amount_min + request.investment_amount_max) / 2
        # )
        
        
        #checks if the company is in prefered sector of the user 
        company_sector_alignment = float(candidate_company.sector in preference.preferred_sectors)
        
        # checks if the valuation fits with the users past 
        valuation_fit = float(preference.valuation_min <= candidate_company.valuation <= preference.valuation_max)
        
        # checks for how mch does the deal close to users preference request
        deal_size_fit = MatchingEngine._range_closeness(candidate_amount, preference.investment_min, preference.investment_max)
        
        # checks for the stage of company
        stage_fit = float(candidate_company.stage in preference.preferred_stages)
        
        price_reasonableness = 0.5
        
        weights = (25, 20, 20, 15, 20)
        
        values = (company_sector_alignment, valuation_fit, deal_size_fit, stage_fit, price_reasonableness)
        
        total = round(sum(value * weight for value, weight in zip(values, weights)), 4)
        
        # Adds reasons to the decision
        reasons = [
            label for value, label in zip(
                values,
                (
                    "Counterparty company matches a preferred sector",
                    "Counterparty valuation fits the preferred range",
                    "Transaction size fits the preferred investment range",
                    "Counterparty company matches a preferred stage",
                    "Price reasonableness is neutral because no comparable price benchmark is available",
                ),
            ) if value > 0
        ]
        return MatchScore(total, company_sector_alignment, valuation_fit, deal_size_fit, stage_fit, price_reasonableness, reasons)

    @staticmethod
    def _range_closeness(value: float, minimum: float, maximum: float) -> float:
        if minimum <= value <= maximum:
            return 1.0
        distance = minimum - value if value < minimum else value - maximum
        span = max(maximum - minimum, maximum, 1.0)
        return max(0.0, 1.0 - distance / span)

    def _preference_or_error(self, user_id: int) -> Preference:
        preference = self.repository.get_preference_for_user(user_id)
        if preference is None:
            raise LookupError(f"No preferences found for user {user_id}")
        return preference

    def _company_or_error(self, company_id: int) -> Company:
        company = self.repository.get_company(company_id)
        if company is None:
            raise LookupError(f"Company with id {company_id} was not found")
        return company
