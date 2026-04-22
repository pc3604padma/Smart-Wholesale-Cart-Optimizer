# Smart Wholesale Cart Optimizer

A complete web-based college project that simulates a wholesale shopping platform and uses the **0/1 Knapsack algorithm (Dynamic Programming)** to optimize item selection within a fixed budget.

## What This Project Does

- Lets shop owners choose item quantities from a preloaded catalog.
- Takes a budget input in rupees.
- Sends selected quantities + budget to FastAPI backend.
- Converts quantities into unit-level items and runs 0/1 Knapsack DP.
- Returns top 3 combinations:
  - Option 1: Maximum items
  - Option 2: Near-optimal
  - Option 3: Alternative selection
- Supports dynamic what-if budget slider and instant recalculation.
- Shows DP table preview and include/exclude steps.

## Folder Structure

```text
Smart-Wholesale-Cart-Optimizer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── catalog.py
│   │   ├── knapsack.py
│   │   ├── main.py
│   │   └── models.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   └── README.md
└── README.md
```

## Quick Start

### 1. Run Backend (FastAPI)

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL: http://127.0.0.1:8000

### 2. Run Frontend (React + Vite)

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: http://127.0.0.1:5173

## Short Knapsack Explanation

In this project, each item unit has:
- weight = price
- value = 1

The budget is the knapsack capacity. The algorithm tries to maximize total value, which means maximizing the number of units selected while staying within budget.

Because users choose quantities, the backend expands each quantity into separate unit items and applies **0/1 Knapsack DP** where every unit can be either selected once or not selected.

If `dp[i][w]` is the max units using first `i` units and capacity `w`, then:

```text
dp[i][w] = max(
  dp[i-1][w],
  dp[i-1][w - price_i] + 1   (if price_i <= w)
)
```

The backend then reconstructs valid selections and returns top 3 combinations.

## Notes

- No database is used; item catalog is static.
- Project is intentionally simple and readable for academic presentation.
