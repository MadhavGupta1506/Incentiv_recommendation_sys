from pathlib import Path
from typing import Any

import pandas as pd


DATASET_SPECS = {
    "companies": {
        "columns": {
            "company_id",
            "name",
            "sector",
            "stage",
            "geography",
            "valuation",
            "quality_score",
            "popularity_score",
            "status",
        },
        "min_rows": 200,
        "max_rows": 200,
    },
    "supplies": {
        "columns": {
            "supply_id",
            "company_id",
            "created_by",
            "units_to_sell",
            "expected_price_per_unit",
            "currency",
            "status",
        },
        "min_rows": 300,
        "max_rows": 500,
    },
    "demands": {
        "columns": {
            "demand_id",
            "company_id",
            "created_by",
            "investment_amount_min",
            "investment_amount_max",
            "currency",
            "status",
        },
        "min_rows": 300,
        "max_rows": 500,
    },
    "preferences": {
        "columns": {
            "preference_id",
            "user_id",
            "primary_sector",
            "secondary_sector",
            "valuation_min",
            "valuation_max",
            "ticket_min",
            "ticket_max",
            "preferred_stage",
            "geography",
        },
        "min_rows": 500,
        "max_rows": 1000,
    },
    "interactions": {
        "columns": {
            "interaction_id",
            "user_id",
            "company_id",
            "event_type",
            "timestamp",
        },
        "min_rows": 15000,
        "max_rows": 30000,
    },
}


def _load_csv(data_dir: Path, name: str) -> pd.DataFrame:
    path = data_dir / f"{name}.csv"
    if not path.exists():
        raise ValueError(f"Missing required dataset: {path}")
    return pd.read_csv(path)


def _validate_shape(name: str, frame: pd.DataFrame, spec: dict[str, Any]) -> None:
    missing_columns = spec["columns"] - set(frame.columns)
    if missing_columns:
        raise ValueError(f"{name} is missing columns: {sorted(missing_columns)}")

    row_count = len(frame)
    if not spec["min_rows"] <= row_count <= spec["max_rows"]:
        raise ValueError(
            f"{name} has {row_count} rows; expected "
            f"{spec['min_rows']}-{spec['max_rows']}"
        )


def _validate_unique_ids(name: str, frame: pd.DataFrame, id_column: str) -> None:
    if frame[id_column].isna().any() or frame[id_column].duplicated().any():
        raise ValueError(f"{name}.{id_column} must contain unique, non-null values")


def _validate_references(
    frame: pd.DataFrame,
    column: str,
    referenced_values: pd.Series,
    label: str,
) -> None:
    if not frame[column].isin(referenced_values).all():
        raise ValueError(f"Invalid company reference in {label}.{column}")


def validate_dataset(data_dir: Path = Path("Data")) -> dict[str, Any]:
    """Validate the supplied synthetic data and return useful profile metrics."""
    datasets = {
        name: _load_csv(data_dir, name) for name in DATASET_SPECS
    }

    for name, frame in datasets.items():
        _validate_shape(name, frame, DATASET_SPECS[name])

    _validate_unique_ids("companies", datasets["companies"], "company_id")
    _validate_unique_ids("supplies", datasets["supplies"], "supply_id")
    _validate_unique_ids("demands", datasets["demands"], "demand_id")
    _validate_unique_ids("preferences", datasets["preferences"], "preference_id")
    _validate_unique_ids("interactions", datasets["interactions"], "interaction_id")

    company_ids = datasets["companies"]["company_id"]
    for name in ("supplies", "demands", "interactions"):
        _validate_references(datasets[name], "company_id", company_ids, name)

    preferences = datasets["preferences"]
    interactions = datasets["interactions"]
    companies = datasets["companies"]
    behavior = (
        interactions.merge(
            companies[["company_id", "sector", "stage"]], on="company_id"
        )
        .merge(
            preferences[["user_id", "primary_sector", "preferred_stage"]],
            on="user_id",
        )
    )
    behavior["sector_match"] = behavior["sector"] == behavior["primary_sector"]
    behavior["stage_match"] = behavior["stage"] == behavior["preferred_stage"]
    alignment = behavior.groupby("event_type")[["sector_match", "stage_match"]].mean()

    if not {"impression", "contact"}.issubset(alignment.index):
        raise ValueError("Interactions must include impression and contact events")
    if not (
        alignment.loc["contact", "sector_match"]
        > alignment.loc["impression", "sector_match"]
        and alignment.loc["contact", "stage_match"]
        > alignment.loc["impression", "stage_match"]
    ):
        raise ValueError("Interaction data does not show the expected preference signal")

    return {
        "row_counts": {name: len(frame) for name, frame in datasets.items()},
        "unique_users": int(preferences["user_id"].nunique()),
        "active_companies": int((companies["status"] == "active").sum()),
        "event_types": sorted(interactions["event_type"].unique().tolist()),
        "contact_sector_match_rate": float(alignment.loc["contact", "sector_match"]),
        "impression_sector_match_rate": float(
            alignment.loc["impression", "sector_match"]
        ),
        "contact_stage_match_rate": float(alignment.loc["contact", "stage_match"]),
        "impression_stage_match_rate": float(
            alignment.loc["impression", "stage_match"]
        ),
    }


if __name__ == "__main__":
    profile = validate_dataset()
    for name, value in profile.items():
        print(f"{name}: {value}")
