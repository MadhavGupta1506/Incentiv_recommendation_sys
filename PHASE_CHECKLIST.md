# Incentiv Recommendation System Phase Checklist

Use this file to track implementation progress. Update it whenever a phase is completed.

## Phase 1 - Project Setup

- [x] Python virtual environment is available at `venv/`.
- [x] FastAPI application package created under `app/`.
- [x] Application startup and shutdown lifespan handling added.
- [x] `GET /health` endpoint added.
- [x] Root `main.py` exports the FastAPI application.
- [x] Phase 1 dependencies declared in `requirements.txt`.
- [x] Phase 1 dependencies installed in the project virtual environment.
- [x] Health endpoint test added and passing.

## Phase 2 - Synthetic Dataset

- [x] Use the supplied CSV files in `Data/` as the synthetic dataset source.
- [x] Validate target row counts and required fields with `scripts/validate_dataset.py`.
- [x] Validate unique IDs and company references across related datasets.
- [x] Confirm interactions contain preference-aligned behavioral signal.

## Phase 3 - Data Models

- [x] Add Pydantic models for companies, supplies, demands, preferences, and interactions.
- [x] Add a Pydantic model for the supplied deals dataset.
- [x] Validate every supplied CSV row against its application model.
- [x] Add cross-field validation for demand and preference ranges.
- [x] Update the preference model for multi-valued sectors, stages, geographies, and deal types.
- [x] Add validation for investment returns, risk, horizon, company age, and ESG preferences.

## Phase 4 - Basic Data APIs

- [x] Add list and detail routes for companies.
- [x] Add list and detail routes for supplies.
- [x] Add list and detail routes for demands.
- [x] Add list and detail routes for preferences.
- [x] Return resource-specific 404 responses for unknown IDs.

## Phase 5 - Candidate Generation

- [x] Add preference-based candidates using multi-valued preferences.
- [x] Add historical-interest candidates weighted by interaction event.
- [x] Add popular candidates as a deterministic fallback.
- [x] Add similar-company candidates using company attributes.
- [x] Merge and deduplicate active candidates.

## Phase 6 - Feature Engineering

- [ ] Add user features.
- [ ] Add company features.
- [ ] Add user-company relationship features.

## Phase 7 - Rule-Based Baseline

- [ ] Implement configurable baseline scoring.
- [ ] Produce baseline recommendations.

## Phase 8 - ML Ranking

- [ ] Add configurable interaction labels.
- [ ] Implement LightGBM learning-to-rank.
- [ ] Rank candidate companies with the trained model.

## Phase 9 - Training Dataset

- [ ] Generate historical user-company training examples.
- [ ] Prevent future-interaction data leakage.

## Phase 10 - Model Evaluation

- [ ] Calculate NDCG@5 and NDCG@10.
- [ ] Calculate Recall@10, Precision@10, and Hit Rate@10.
- [ ] Compare baseline and ML ranking results.

## Phase 11 - Recommendation Engine

- [ ] Add the recommendation orchestrator.
- [ ] Support `get_recommendations(user_id, limit=10)`.
- [ ] Return ranked top-K recommendations.

## Phase 12 - Business Re-Ranking

- [ ] Remove inactive or unavailable companies.
- [ ] Apply diversity rules.
- [ ] Keep business constraints separate from ML scoring.

## Phase 13 - Recommendation Explanations

- [ ] Return score breakdowns.
- [ ] Return human-readable recommendation reasons.

## Phase 14 - Cold Start

- [ ] Handle users without interaction history.
- [ ] Handle new companies using metadata and preferences.

## Phase 15 - Testing

- [ ] Add API tests for all required routes.
- [ ] Add recommendation-engine tests.
- [ ] Add model training and persistence tests.

## Phase 16 - Demo and Documentation

- [ ] Add an end-to-end demo script.
- [ ] Document local setup and run commands.
- [ ] Verify the complete demo flow.
- [ ] Commit each completed feature to GitHub.
