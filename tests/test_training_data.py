from app.recommendation.ml_ranking import InteractionLabels
from app.recommendation.training_data import TrainingDataBuilder


def test_builds_training_rows_and_lightgbm_groups() -> None:
    training_data = TrainingDataBuilder().build()

    assert len(training_data.features) == 21080
    assert len(training_data.labels) == 21080
    assert sum(training_data.groups) == 21080
    assert len(training_data.groups) == 500
    assert set(training_data.labels).issubset({0, 1, 2, 3, 4, 5})
    assert training_data.features.select_dtypes(exclude="number").empty


def test_custom_labels_are_used() -> None:
    training_data = TrainingDataBuilder(
        labels=InteractionLabels(impression=10, contact=20)
    ).build()

    assert 10 in training_data.labels
    assert 20 in training_data.labels


def test_first_event_has_no_prior_history() -> None:
    training_data = TrainingDataBuilder().build()
    first_user_row = training_data.user_ids.index(1)

    assert training_data.features.iloc[first_user_row]["historical_interaction_count"] == 0
    assert training_data.features.iloc[first_user_row]["historical_interest"] == 0
