from time import perf_counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .catalog import CATALOG_ITEMS, CATALOG_MAP
from .knapsack import expand_units, optimize_with_knapsack
from .models import OptimizeRequest


app = FastAPI(title="Smart Wholesale Cart Optimizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/catalog")
def get_catalog() -> dict[str, list[dict]]:
    return {"items": CATALOG_ITEMS}


@app.post("/api/optimize")
def optimize_cart(payload: OptimizeRequest) -> dict:
    unknown_ids = [item.item_id for item in payload.cart_items if item.item_id not in CATALOG_MAP]
    if unknown_ids:
        raise HTTPException(status_code=400, detail=f"Unknown item ids: {', '.join(unknown_ids)}")

    units = expand_units([item.model_dump() for item in payload.cart_items], CATALOG_MAP)

    try:
        started_at = perf_counter()
        result = optimize_with_knapsack(units, payload.budget, payload.include_visualization)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    elapsed_ms = round((perf_counter() - started_at) * 1000, 2)
    result.setdefault("metadata", {})
    result["metadata"]["time_taken_ms"] = elapsed_ms

    return result
