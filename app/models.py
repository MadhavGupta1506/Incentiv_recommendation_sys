from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


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
    primary_sector: Sector
    secondary_sector: Sector
    valuation_min: float = Field(ge=0)
    valuation_max: float = Field(ge=0)
    ticket_min: float = Field(ge=0)
    ticket_max: float = Field(ge=0)
    preferred_stage: Stage
    geography: Geography

    @model_validator(mode="after")
    def validate_preference_ranges(self) -> "Preference":
        if self.valuation_min > self.valuation_max:
            raise ValueError("valuation_min cannot exceed valuation_max")
        if self.ticket_min > self.ticket_max:
            raise ValueError("ticket_min cannot exceed ticket_max")
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
