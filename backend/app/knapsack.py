from collections import defaultdict
from dataclasses import dataclass
from functools import reduce
from math import gcd
from typing import Any


@dataclass
class UnitItem:
    unit_id: str
    item_id: str
    name: str
    price: int


def _price_unit(prices: list[int], budget: int) -> int:
    values = [value for value in prices + [budget] if value > 0]
    if not values:
        return 1
    return max(1, reduce(gcd, values))


def expand_units(cart_items: list[dict[str, Any]], catalog_map: dict[str, dict[str, Any]]) -> list[UnitItem]:
    expanded: list[UnitItem] = []

    for cart_item in cart_items:
        item_id = cart_item["item_id"]
        quantity = cart_item["quantity"]
        catalog_item = catalog_map.get(item_id)

        if not catalog_item or quantity <= 0:
            continue

        for index in range(quantity):
            expanded.append(
                UnitItem(
                    unit_id=f"{item_id}__{index + 1}",
                    item_id=item_id,
                    name=catalog_item["name"],
                    price=int(catalog_item["price"]),
                )
            )

    return expanded


def _build_solution(selected_units: list[UnitItem], budget: int) -> dict[str, Any]:
    grouped: dict[str, dict[str, Any]] = defaultdict(lambda: {"name": "", "quantity": 0, "unit_price": 0, "subtotal": 0})

    for unit in selected_units:
        bucket = grouped[unit.item_id]
        bucket["name"] = unit.name
        bucket["quantity"] += 1
        bucket["unit_price"] = unit.price
        bucket["subtotal"] += unit.price

    items = [
        {
            "item_id": item_id,
            "name": data["name"],
            "quantity": data["quantity"],
            "unit_price": data["unit_price"],
            "subtotal": data["subtotal"],
        }
        for item_id, data in grouped.items()
    ]
    items.sort(key=lambda value: (value["name"], value["item_id"]))

    total_cost = sum(item["subtotal"] for item in items)
    total_items = sum(item["quantity"] for item in items)

    return {
        "items": items,
        "total_cost": total_cost,
        "total_items": total_items,
        "budget": budget,
        "budget_usage_percent": round((total_cost / budget) * 100, 2) if budget > 0 else 0,
    }


def _build_dp(units: list[UnitItem], budget: int, unit_value: int) -> tuple[list[list[int]], list[int], int]:
    weights = [max(1, unit.price // unit_value) for unit in units]
    capacity = max(0, budget // unit_value)
    n = len(units)

    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        weight = weights[i - 1]
        for w in range(capacity + 1):
            best_without = dp[i - 1][w]
            best_with = -1
            if weight <= w:
                best_with = dp[i - 1][w - weight] + 1
            dp[i][w] = max(best_without, best_with)

    return dp, weights, capacity


def _collect_solutions(
    units: list[UnitItem],
    dp: list[list[int]],
    weights: list[int],
    capacity: int,
    budget: int,
    max_solutions: int = 30,
) -> list[dict[str, Any]]:
    n = len(units)
    solutions: dict[tuple[tuple[str, int], ...], dict[str, Any]] = {}
    seen_states: set[tuple[int, int, tuple[int, ...]]] = set()

    # DFS over include/exclude choices guided by DP optimality relations.
    stack: list[tuple[int, int, list[int]]] = [(n, capacity, [])]

    while stack and len(solutions) < max_solutions:
        i, w, chosen_indices = stack.pop()
        state_key = (i, w, tuple(sorted(chosen_indices)))
        if state_key in seen_states:
            continue
        seen_states.add(state_key)

        if i == 0:
            selected_units = [units[index] for index in chosen_indices]
            if sum(unit.price for unit in selected_units) > budget:
                continue

            solution = _build_solution(selected_units, budget)
            signature = tuple(sorted((item["item_id"], item["quantity"]) for item in solution["items"]))
            if signature not in solutions:
                solutions[signature] = solution
            continue

        weight = weights[i - 1]
        current = dp[i][w]

        if dp[i - 1][w] == current:
            stack.append((i - 1, w, chosen_indices.copy()))

        if weight <= w and dp[i - 1][w - weight] + 1 == current:
            include_list = chosen_indices.copy()
            include_list.append(i - 1)
            stack.append((i - 1, w - weight, include_list))

    result = list(solutions.values())
    result.sort(key=lambda sol: (sol["total_items"], sol["total_cost"], len(sol["items"])), reverse=True)
    return result


def _build_steps_for_solution(units: list[UnitItem], weights: list[int], dp: list[list[int]], capacity: int) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    i = len(units)
    w = capacity

    while i > 0:
        unit = units[i - 1]
        weight = weights[i - 1]

        if weight <= w and dp[i][w] == dp[i - 1][w - weight] + 1 and dp[i][w] >= dp[i - 1][w]:
            decision = "include"
            previous_w = w
            w = w - weight
            details = f"Included {unit.name} (Rs.{unit.price}) because it improves item count."
        else:
            decision = "exclude"
            previous_w = w
            details = f"Excluded {unit.name} (Rs.{unit.price}) because skipping keeps best score."

        steps.append(
            {
                "step": len(units) - i + 1,
                "item": unit.name,
                "item_price": unit.price,
                "decision": decision,
                "capacity_before": previous_w,
                "capacity_after": w,
                "best_items_now": dp[i][previous_w],
                "details": details,
            }
        )
        i -= 1

    return steps


def _build_traceback_path(
    units: list[UnitItem], weights: list[int], dp: list[list[int]], capacity: int
) -> list[dict[str, Any]]:
    path: list[dict[str, Any]] = []
    i = len(units)
    w = capacity

    while i > 0:
        unit = units[i - 1]
        weight = weights[i - 1]

        if weight <= w and dp[i][w] == dp[i - 1][w - weight] + 1 and dp[i][w] >= dp[i - 1][w]:
            decision = "include"
            path.append({"row": i, "col": w, "decision": decision, "item": unit.name})
            w -= weight
        else:
            decision = "exclude"
            path.append({"row": i, "col": w, "decision": decision, "item": unit.name})

        i -= 1

    path.append({"row": 0, "col": w, "decision": "start", "item": "Start"})
    return path


def optimize_with_knapsack(units: list[UnitItem], budget: int, include_visualization: bool = True) -> dict[str, Any]:
    if budget <= 0:
        raise ValueError("Budget must be greater than zero.")

    if not units:
        return {
            "best_option": _build_solution([], budget),
            "top_options": [],
            "metadata": {"message": "No selectable units available."},
            "visualization": None,
        }

    divisor = _price_unit([unit.price for unit in units], budget)
    dp, weights, capacity = _build_dp(units, budget, divisor)
    all_best = _collect_solutions(units, dp, weights, capacity, budget)

    if not all_best:
        all_best = [_build_solution([], budget)]

    best_count = all_best[0]["total_items"]
    near_candidates = [sol for sol in all_best if sol["total_items"] >= max(0, best_count - 1)]

    # Ensure at least 3 candidate choices when possible.
    options = near_candidates[:3]
    if len(options) < 3:
        remaining = [sol for sol in all_best if sol not in options]
        options.extend(remaining[: 3 - len(options)])

    labeled_options = []
    labels = ["Option 1: Maximum items", "Option 2: Near-optimal", "Option 3: Alternative selection"]
    for index, option in enumerate(options):
        option_copy = option.copy()
        option_copy["label"] = labels[index] if index < len(labels) else f"Option {index + 1}"
        labeled_options.append(option_copy)

    best_option = labeled_options[0] if labeled_options else _build_solution([], budget)

    visualization = None
    if include_visualization:
        rows_limit = min(len(dp), 18)
        cols_limit = min(len(dp[0]) if dp else 0, 28)
        row_offset = max(0, len(dp) - rows_limit)
        col_offset = max(0, (len(dp[0]) if dp else 0) - cols_limit)
        table_preview = [row[col_offset : col_offset + cols_limit] for row in dp[row_offset : row_offset + rows_limit]]

        visualization = {
            "price_divisor": divisor,
            "capacity_scaled": capacity,
            "table_preview": table_preview,
            "row_offset": row_offset,
            "col_offset": col_offset,
            "rows_shown": rows_limit,
            "columns_shown": cols_limit,
            "table_truncated": rows_limit < len(dp) or (cols_limit < len(dp[0]) if dp else False),
            "decision_steps": _build_steps_for_solution(units, weights, dp, capacity)[:40],
            "traceback_path": _build_traceback_path(units, weights, dp, capacity),
        }

    return {
        "best_option": best_option,
        "top_options": labeled_options,
        "metadata": {
            "expanded_units_count": len(units),
            "max_items": best_option.get("total_items", 0),
            "algorithm": "0/1 Knapsack (Dynamic Programming)",
            "time_complexity": "O(nW)",
        },
        "visualization": visualization,
    }
