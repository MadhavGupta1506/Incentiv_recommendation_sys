from fastapi import APIRouter, HTTPException, Query

from app.matching.engine import MatchingEngine, SupplyDemandMatch


router = APIRouter(prefix="/matches", tags=["matches"])
engine = MatchingEngine()


def _serialize(match: SupplyDemandMatch) -> dict[str, object]:

    return {
        "supply": match.supply.model_dump(),
        "demand": match.demand.model_dump(),
        "supply_company": match.supply_company.model_dump(),
        "demand_company": match.demand_company.model_dump(),
        "score": match.score.total_score,
        "score_breakdown": {
            "company_sector_alignment": match.score.company_sector_alignment,
            "valuation_fit": match.score.valuation_fit,
            "deal_size_fit": match.score.deal_size_fit,
            "stage_fit": match.score.stage_fit,
            "price_reasonableness": match.score.price_reasonableness,
        },
        "reasons": match.score.reasons,
    }


@router.get("/supply/{supply_id}")
def match_supply(
    supply_id: int,
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, object]]:
    try:
        return [_serialize(match) for match in engine.match_supply(supply_id, limit)]
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/demand/{demand_id}")
def match_demand(
    demand_id: int,
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, object]]:
    try:
        return [_serialize(match) for match in engine.match_demand(demand_id, limit)]
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
