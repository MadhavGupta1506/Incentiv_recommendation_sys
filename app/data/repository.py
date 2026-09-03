import csv
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.models import Company, Demand, Preference, Supply


ModelType = TypeVar("ModelType", bound=BaseModel)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class DataRepository:
    """Read and index the local CSV datasets used by the API."""

    def __init__(self, data_dir: Path = PROJECT_ROOT / "Data") -> None:
        self.companies = self._load("companies.csv", Company, data_dir)
        self.supplies = self._load("supplies.csv", Supply, data_dir)
        self.demands = self._load("demands.csv", Demand, data_dir)
        self.preferences = self._load("preferences.csv", Preference, data_dir)

    @staticmethod
    def _load(
        filename: str,
        model: type[ModelType],
        data_dir: Path,
    ) -> list[ModelType]:
        path = data_dir / filename
        with path.open(newline="", encoding="utf-8") as csv_file:
            return [model.model_validate(row) for row in csv.DictReader(csv_file)]

    def get_companies(self) -> list[Company]:
        return self.companies

    def get_company(self, company_id: int) -> Company | None:
        return next((item for item in self.companies if item.company_id == company_id), None)

    def get_supplies(self) -> list[Supply]:
        return self.supplies

    def get_supply(self, supply_id: int) -> Supply | None:
        return next((item for item in self.supplies if item.supply_id == supply_id), None)

    def get_demands(self) -> list[Demand]:
        return self.demands

    def get_demand(self, demand_id: int) -> Demand | None:
        return next((item for item in self.demands if item.demand_id == demand_id), None)

    def get_preferences(self) -> list[Preference]:
        return self.preferences

    def get_preference(self, preference_id: int) -> Preference | None:
        return next(
            (item for item in self.preferences if item.preference_id == preference_id),
            None,
        )


repository = DataRepository()
