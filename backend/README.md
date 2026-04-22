# Backend - Smart Wholesale Cart Optimizer

FastAPI backend implementing 0/1 Knapsack using Dynamic Programming.

## Endpoints

- `GET /api/health` : health check
- `GET /api/catalog` : returns static wholesale catalog
- `POST /api/optimize` : runs knapsack optimization

## Request Body Example

```json
{
  "budget": 7000,
  "cart_items": [
    { "item_id": "rice_bag", "quantity": 1 },
    { "item_id": "tea_bundle", "quantity": 2 },
    { "item_id": "veg_pack", "quantity": 3 }
  ],
  "include_visualization": true
}
```

## How Optimization Works

1. Validate budget and item IDs.
2. Expand quantity-based cart to unit-level item list.
3. Run 0/1 Knapsack DP where:
   - weight = unit price
   - value = 1 for each unit
4. Backtrack DP choices to produce valid combinations.
5. Return top 3 options and optional visualization data.

## Run Backend

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Runs on http://127.0.0.1:8000
