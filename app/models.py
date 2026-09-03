from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field, model_validator


Sector = Literal[
    "FinTech",
    "SaaS",
    "HealthTech",
    "EdTech",
    "E-commerce",
    "ClimateTech",
    "AI/ML",
    "Logistics",
]
Stage = Literal["Pre-Seed", "Seed", "Series A", "Series B", "Series C"]
Geography = Literal["India", "USA", "UK", "Singapore", "UAE"]
DealType = Literal["Primary Equity", "Secondary", "Convertible", "Debt"]
RiskAppetite = Literal["Low", "Medium", "High"]
InvestmentHorizon = Literal["<2 years", "2-5 years", "5-8 years", "8+ years"]
CompanyStatus = Literal["active", "inactive", "closed"]
OpportunityStatus = Literal["active", "closed"]
EventType = Literal[
    "impression",
    "view",
    "click",
    "save",
    "shortlist",
    "contact",
]
DealStatus = Literal["completed", "cancelled"]


def _split_csv_values(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.split("|") if item.strip()]
    return value


SectorList = Annotated[list[Sector], BeforeValidator(_split_csv_values)]
StageList = Annotated[list[Stage], BeforeValidator(_split_csv_values)]
GeographyList = Annotated[list[Geography], BeforeValidator(_split_csv_values)]
DealTypeList = Annotated[list[DealType], BeforeValidator(_split_csv_values)]


class Company(BaseModel):
    company_id: int = Field(gt=0)
    name: str = Field(min_length=1)
    sector: Sector
    stage: Stage
    geography: Geography
    valuation: float = Field(ge=0)
    quality_score: float = Field(ge=0, le=1)
    popularity_score: float = Field(ge=0, le=1)
    status: CompanyStatus


class Supply(BaseModel):
    supply_id: int = Field(gt=0)
    company_id: int = Field(gt=0)
    created_by: int = Field(gt=0)
    units_to_sell: int = Field(gt=0)
    expected_price_per_unit: float = Field(gt=0)
    currency: str = Field(min_length=1)
    status: OpportunityStatus


class Demand(BaseModel):
    demand_id: int = Field(gt=0)
    company_id: int = Field(gt=0)
    created_by: int = Field(gt=0)
    investment_amount_min: float = Field(ge=0)
    investment_amount_max: float = Field(ge=0)
    currency: str = Field(min_length=1)
    status: OpportunityStatus

    @model_validator(mode="after")
    def validate_amount_range(self) -> "Demand":
        if self.investment_amount_min > self.investment_amount_max:
            raise ValueError("investment_amount_min cannot exceed investment_amount_max")
        return self


class Preference(BaseModel):
    preference_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    preferred_sectors: SectorList = Field(min_length=1)
    preferred_stages: StageList = Field(min_length=1)
    preferred_geographies: GeographyList = Field(min_length=1)
    investment_min: float = Field(ge=0)
    investment_max: float = Field(ge=0)
    valuation_min: float = Field(ge=0)
    valuation_max: float = Field(ge=0)
    preferred_deal_types: DealTypeList = Field(min_length=1)
    min_expected_return_pct: float = Field(ge=0, le=100)
    risk_appetite: RiskAppetite
    investment_horizon: InvestmentHorizon
    company_age_min_years: int = Field(ge=0)
    company_age_max_years: int = Field(ge=0)
    esg_preference: bool

    @model_validator(mode="after")
    def validate_preference_ranges(self) -> "Preference":
        if self.valuation_min > self.valuation_max:
            raise ValueError("valuation_min cannot exceed valuation_max")
        if self.investment_min > self.investment_max:
            raise ValueError("investment_min cannot exceed investment_max")
        if self.company_age_min_years > self.company_age_max_years:
            raise ValueError(
                "company_age_min_years cannot exceed company_age_max_years"
            )
        return self


class Interaction(BaseModel):
    interaction_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    company_id: int = Field(gt=0)
    event_type: EventType
    timestamp: datetime


class Deal(BaseModel):
    deal_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    company_id: int = Field(gt=0)
    deal_amount: float = Field(gt=0)
    currency: str = Field(min_length=1)
    deal_status: DealStatus
    deal_date: datetime
