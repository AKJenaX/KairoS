from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import csv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents import (
    CapacityAgent,
    DemandAgent,
    ErrorDetectionAgent,
    InventoryAgent,
    LayoutAgent,
    StoreAllocationAgent,
)


app = FastAPI(title="MALO Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

demand_agent = DemandAgent()
store_allocation_agent = StoreAllocationAgent()
inventory_agent = InventoryAgent()
layout_agent = LayoutAgent()
capacity_agent = CapacityAgent()
error_detection_agent = ErrorDetectionAgent()


def load_sample_data() -> List[Dict[str, str]]:
    data_path = Path(__file__).resolve().parents[1] / "data" / "sample_data.csv"
    with data_path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


class DemandRequest(BaseModel):
    rainfall: int = Field(ge=0, le=200)
    festival: bool


class StoreLoadItem(BaseModel):
    store: str
    load: float = Field(ge=0)


class AllocationRequest(BaseModel):
    store_load: List[StoreLoadItem]
    distance: Dict[str, float]
    inventory: Dict[str, int]


class InventoryRequest(BaseModel):
    stock_levels: Dict[str, int]


class LayoutRequest(BaseModel):
    picking_frequency: Dict[str, int]


class CapacityRequest(BaseModel):
    demand: int
    capacity: int


class ErrorRequest(BaseModel):
    expected_item: str
    scanned_item: str


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "MALO backend is running"}


@app.get("/sample-data")
def sample_data() -> Dict[str, List[Dict[str, str]]]:
    return {"records": load_sample_data()}


@app.post("/predict-demand")
def predict_demand(payload: DemandRequest) -> Dict:
    demand_level = demand_agent.predict(payload.rainfall, payload.festival)
    return {
        "agent": "Demand Agent",
        "demand_level": demand_level,
        "inputs": payload.model_dump(),
    }


@app.post("/allocate-store")
def allocate_store(payload: AllocationRequest) -> Dict:
    result = store_allocation_agent.allocate(
        store_load=[item.model_dump() for item in payload.store_load],
        distance=payload.distance,
        inventory=payload.inventory,
    )
    return {"agent": "Store Allocation Agent", "inputs": payload.model_dump(), "result": result}


@app.post("/balance-inventory")
def balance_inventory(payload: InventoryRequest) -> Dict:
    result = inventory_agent.balance(payload.stock_levels)
    return {"agent": "Inventory Agent", "inputs": payload.model_dump(), "result": result}


@app.post("/optimize-layout")
def optimize_layout(payload: LayoutRequest) -> Dict:
    result = layout_agent.optimize(payload.picking_frequency)
    return {"agent": "Layout Optimization Agent", "inputs": payload.model_dump(), "result": result}


@app.post("/activate-capacity")
def activate_capacity(payload: CapacityRequest) -> Dict:
    result = capacity_agent.evaluate(payload.demand, payload.capacity)
    return {"agent": "Capacity Agent", "inputs": payload.model_dump(), "result": result}


@app.post("/check-error")
def check_error(payload: ErrorRequest) -> Dict:
    result = error_detection_agent.check(
        expected_item=payload.expected_item,
        scanned_item=payload.scanned_item,
    )
    return {"agent": "Error Detection Agent", "inputs": payload.model_dump(), "result": result}
