# Frontend - Smart Wholesale Cart Optimizer

React frontend with a clean and colorful responsive UI.

## Features

- Budget input and validation
- Dynamic what-if budget slider
- Item catalog cards with + and - quantity controls
- Cart summary with total cost and over-budget warning
- Optimize button to call backend knapsack API
- Top 3 solution cards
- Knapsack process visualization mode:
  - DP table preview
  - include/exclude step list
- Bonus stats:
  - budget usage percentage
  - total selected units

## Setup

```bash
npm install
npm run dev
```

Runs on http://127.0.0.1:5173

## API Dependency

The app expects backend FastAPI server at:

- http://127.0.0.1:8000

If needed, update `API_BASE` in `src/App.jsx`.
