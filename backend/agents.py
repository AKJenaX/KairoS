from __future__ import annotations

from typing import Dict, List


class DemandAgent:
    def predict(self, rainfall: int, festival: bool) -> str:
        score = 0
        if rainfall >= 70:
            score += 2
        elif rainfall >= 35:
            score += 1

        if festival:
            score += 2

        if score >= 3:
            return "HIGH"
        if score >= 1:
            return "MEDIUM"
        return "LOW"


class StoreAllocationAgent:
    def allocate(self, store_load: List[Dict], distance: Dict[str, float], inventory: Dict[str, int]) -> Dict:
        best_store = None
        best_score = float("-inf")
        scored_stores = []

        for store in store_load:
            store_name = store["store"]
            load = float(store["load"])
            distance_km = float(distance.get(store_name, 999))
            stock = int(inventory.get(store_name, 0))

            score = (stock * 1.5) - (load * 0.7) - (distance_km * 2.0)
            scored_stores.append(
                {
                    "store": store_name,
                    "load": load,
                    "distance_km": distance_km,
                    "inventory": stock,
                    "score": round(score, 2),
                }
            )

            if stock > 0 and score > best_score:
                best_score = score
                best_store = store_name

        if best_store is None:
            best_store = "No feasible store"

        return {"selected_store": best_store, "store_scores": scored_stores}


class InventoryAgent:
    def balance(self, stock_levels: Dict[str, int]) -> Dict:
        if not stock_levels:
            return {"transfer_recommendation": "No stock data available", "actions": []}

        highest_store = max(stock_levels, key=stock_levels.get)
        lowest_store = min(stock_levels, key=stock_levels.get)
        high_stock = stock_levels[highest_store]
        low_stock = stock_levels[lowest_store]

        if high_stock - low_stock < 15:
            return {
                "transfer_recommendation": "Stock levels are already balanced",
                "actions": [],
            }

        transfer_units = max(5, (high_stock - low_stock) // 2)
        recommendation = (
            f"Transfer {transfer_units} units from {highest_store} to {lowest_store}"
        )
        return {
            "transfer_recommendation": recommendation,
            "actions": [
                {
                    "from_store": highest_store,
                    "to_store": lowest_store,
                    "units": transfer_units,
                }
            ],
        }


class LayoutAgent:
    def optimize(self, picking_frequency: Dict[str, int]) -> Dict:
        sorted_items = sorted(
            picking_frequency.items(), key=lambda item: item[1], reverse=True
        )
        zone_order = ["Front Shelf", "Mid Shelf", "Side Rack", "Back Shelf", "Top Rack"]
        placements = []

        for index, (item_name, picks) in enumerate(sorted_items):
            placements.append(
                {
                    "item": item_name,
                    "picking_frequency": picks,
                    "new_position": zone_order[min(index, len(zone_order) - 1)],
                }
            )

        return {"new_shelf_positions": placements}


class CapacityAgent:
    def evaluate(self, demand: int, capacity: int) -> Dict:
        utilization = 0.0 if capacity <= 0 else round((demand / capacity) * 100, 2)
        activate = capacity <= 0 or demand > capacity
        reason = (
            "Demand exceeds live-store capacity"
            if activate
            else "Current store network can absorb demand"
        )
        return {
            "activate_ghost_store": activate,
            "utilization_percent": utilization,
            "reason": reason,
        }


class ErrorDetectionAgent:
    def check(self, expected_item: str, scanned_item: str) -> Dict:
        normalized_expected = expected_item.strip().lower()
        normalized_scanned = scanned_item.strip().lower()
        success = normalized_expected == normalized_scanned

        return {
            "status": "success" if success else "error",
            "message": (
                "Picked item matches the order"
                if success
                else f"Mismatch detected: expected '{expected_item}', scanned '{scanned_item}'"
            ),
        }
