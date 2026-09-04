# Incentiv Recommendation System

A locally runnable recommendation-system demo using the CSV data in `Data/`.

## Setup

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run The API

```powershell
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

Useful requests:

```text
GET /health
GET /companies
GET /preferences/1
GET /recommendations/1?limit=10
GET /recommendations/999999?limit=10
```

The recommendation endpoint uses the explainable baseline by default. The ML option is available after a trained ranker is supplied by application code:

```text
GET /recommendations/1?model=ml&limit=10
```

## Run The Demo

The demo validates the point-in-time training data, trains LightGBM, compares baseline and ML metrics, saves `model/ranker.txt`, and prints recommendations:

```powershell
.\venv\Scripts\python.exe scripts\demo_recommendations.py
```

## Data

The application uses local CSV files:

- `companies.csv`: 200 companies and metadata
- `supplies.csv`: 500 available opportunities
- `demands.csv`: 500 investment requirements
- `preferences.csv`: 500 multi-valued user preference profiles
- `interactions.csv`: 21,080 historical events
- `deals.csv`: 450 deal outcomes

No database, authentication, or external infrastructure is required.

## Architecture

```text
CSV files -> Pydantic models -> repository
          -> candidate generation -> feature engineering
          -> baseline or LightGBM ranking -> business re-ranking
          -> explained recommendations
```

The implementation is split into independent modules under `app/recommendation/` for candidate generation, features, ranking, training data, ML ranking, evaluation, re-ranking, and orchestration. Progress is tracked in `PHASE_CHECKLIST.md`.

## Tests

```powershell
.\venv\Scripts\python.exe -m pytest -q
```
