from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError

from app.models import Company, Demand, Interaction, Preference, Supply


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "Data"


def _records(name: str) -> list[dict[str, object]]:
    return pd.read_csv(DATA_DIR / f"{name}.csv").to_dict(orient="records")


def test_all_supplied_rows_validate_against_application_models() -> None:
    model_rows = {
        "companies": (Company, _records("companies")),
        "supplies": (Supply, _records("supplies")),
        "demands": (Demand, _records("demands")),
        "preferences": (Preference, _records("preferences")),
        "interactions": (Interaction, _records("interactions")),
    }

    for model, rows in model_rows.values():
        validated_rows = [model.model_validate(row) for row in rows]
        assert len(validated_rows) == len(rows)


def test_demand_rejects_reversed_amount_range() -> None:
    row = _records("demands")[0]
    row["investment_amount_min"] = row["investment_amount_max"] + 1

    with pytest.raises(ValidationError, match="investment_amount_min"):
        Demand.model_validate(row)


def test_preference_rejects_reversed_ticket_range() -> None:
    row = _records("preferences")[0]
    row["ticket_min"] = row["ticket_max"] + 1

    with pytest.raises(ValidationError, match="ticket_min"):
        Preference.model_validate(row)
