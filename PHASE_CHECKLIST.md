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
- [x] Keep each resource's API routes in a separate module with a shared router aggregator.

## Phase 5 - Candidate Generation

- [x] Add preference-based candidates using multi-valued preferences.
- [x] Add historical-interest candidates weighted by interaction event.
- [x] Add popular candidates as a deterministic fallback.
- [x] Add similar-company candidates using company attributes.
- [x] Merge and deduplicate active candidates.

## Phase 6 - Feature Engineering

- [x] Add user profile features from the updated preference schema and interaction history.
- [x] Add company metadata features.
- [x] Add user-company relationship features.
- [x] Keep feature generation independent from ranking weights and business rules.

## Phase 7 - Rule-Based Baseline

- [x] Implement configurable baseline scoring with normalized 0-100 output.
- [x] Produce deterministic ranked baseline recommendations.
- [x] Return per-dimension score breakdowns and human-readable reasons.

## Phase 8 - ML Ranking

- [x] Add configurable interaction labels.
- [x] Implement LightGBM learning-to-rank with grouped training data.
- [x] Save and load trained LightGBM models.
- [x] Rank candidate companies with the trained model.

## Phase 9 - Training Dataset

- [x] Generate historical user-company training examples from interaction events.
- [x] Produce LightGBM-compatible user ranking groups.
- [x] Prevent current and future interaction data leakage with point-in-time features.

## Phase 10 - Model Evaluation

- [x] Calculate NDCG@5 and NDCG@10.
- [x] Calculate Recall@10, Precision@10, and Hit Rate@10.
- [x] Compare baseline and ML ranking results.
- [x] Aggregate metrics per user ranking group with configurable positive relevance.

## Phase 11 - Recommendation Engine

- [x] Add the recommendation orchestrator.
- [x] Support `get_recommendations(user_id, limit=10)`.
- [x] Return ranked top-K recommendations through the baseline or ML model.
- [x] Expose baseline recommendations through `GET /recommendations/{user_id}`.

## Phase 12 - Business Re-Ranking

- [x] Remove inactive or unavailable companies.
- [x] Apply a configurable per-sector diversity limit.
- [x] Keep business constraints separate from ML scoring.

## Phase 13 - Recommendation Explanations

- [x] Return baseline score breakdowns.
- [x] Return human-readable recommendation reasons.
- [x] Return candidate source provenance.

## Phase 14 - Cold Start

- [x] Handle users without interaction history with popular-company fallback.
- [x] Use company metadata and preference matching for candidates without history.

## Phase 15 - Testing

- [x] Add API tests for all implemented routes.
- [x] Add recommendation-engine and business re-ranking tests.
- [x] Add model training and persistence tests.

## Phase 16 - Demo and Documentation

- [x] Add an end-to-end demo script.
- [ ] Document local setup and run commands.
- [x] Verify the complete demo flow.
- [x] Commit each completed feature to GitHub.

## Buyer-Seller Matching Engine

- [x] Match a supply row to ranked demand rows.
- [x] Match a demand row to ranked supply rows.
- [x] Resolve the requesting user's own preferences only.
- [x] Enforce active status and same-currency eligibility.
- [x] Score sector alignment, valuation fit, deal size fit, stage fit, and price reasonableness.
- [x] Return buyer-seller pairs with score breakdowns and reasons.
- [x] Keep matching routes modular under `app/api/matches.py`.
- [x] Keep automated deal creation out of scope.
