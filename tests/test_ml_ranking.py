from pathlib import Path

import pandas as pd
import pytest

from app.recommendation.ml_ranking import InteractionLabels, LightGBMRanker


def _training_data() -> tuple[pd.DataFrame, list[int], list[int]]:
    features = pd.DataFrame(
        {
            "sector_match": [1, 0, 0, 0, 1, 0, 0, 1],
            "stage_match": [1, 0, 0, 1, 1, 0, 1, 0],
            "company_popularity_score": [0.9, 0.2, 0.3, 0.4, 0.8, 0.1, 0.4, 0.7],
        }
    )
    return features, [5, 0, 1, 4, 4, 0, 2, 1], [4, 4]


def test_interaction_labels_are_configurable() -> None:
    labels = InteractionLabels(contact=10, save=7)

    assert labels.label_for("contact") == 10
    assert labels.label_for("save") == 7
    assert LightGBMRanker.labels_from_events(["impression", "contact"], labels) == [0, 10]

    with pytest.raises(ValueError, match="Unsupported"):
        labels.label_for("unknown")


def test_trains_and_predicts_grouped_rankings() -> None:
    features, labels, groups = _training_data()
    ranker = LightGBMRanker(model_params={"n_estimators": 10}).train(
        features, labels, groups
    )

    predictions = ranker.predict(features)

    assert ranker.is_fitted
    assert len(predictions) == len(features)
    assert len(set(predictions)) > 1


def test_model_can_be_saved_and_loaded(tmp_path: Path) -> None:
    features, labels, groups = _training_data()
    ranker = LightGBMRanker(model_params={"n_estimators": 10}).train(
        features, labels, groups
    )
    model_path = tmp_path / "ranker.txt"
    ranker.save(model_path)
    loaded = LightGBMRanker.load(model_path)

    assert loaded.predict(features) == pytest.approx(ranker.predict(features))


def test_training_input_is_validated() -> None:
    features, labels, groups = _training_data()

    with pytest.raises(ValueError, match="same length"):
        LightGBMRanker().train(features, labels[:-1], groups)
    with pytest.raises(ValueError, match="sum"):
        LightGBMRanker().train(features, labels, [3, 3])
