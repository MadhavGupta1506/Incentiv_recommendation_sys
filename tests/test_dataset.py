from pathlib import Path

import pandas as pd

from scripts.validate_dataset import validate_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_supplied_dataset_matches_phase_two_requirements() -> None:
    profile = validate_dataset(PROJECT_ROOT / "Data")

    assert profile["row_counts"] == {
        "companies": 200,
        "supplies": 500,
        "demands": 500,
        "preferences": 500,
        "interactions": 21080,
    }
    assert profile["unique_users"] == 500
    assert profile["active_companies"] == 188


def test_preferences_define_one_profile_per_user_with_multiple_choices() -> None:
    preferences = pd.read_csv(PROJECT_ROOT / "Data" / "preferences.csv")

    assert preferences["user_id"].is_unique
    assert preferences["preferred_sectors"].str.contains("\\|").any()
    assert preferences["preferred_stages"].str.contains("\\|").any()


def test_interactions_contain_preference_signal() -> None:
    profile = validate_dataset(PROJECT_ROOT / "Data")

    assert profile["contact_sector_match_rate"] > profile["impression_sector_match_rate"]
    assert profile["contact_stage_match_rate"] > profile["impression_stage_match_rate"]
