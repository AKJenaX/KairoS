# Multi-Agent Autonomous Logistics Orchestrator (MALO)

MALO is a ready-to-run quick-commerce simulation built with FastAPI and Streamlit. It models a logistics backend with six rule-based AI agents that detect demand surges, allocate stores, rebalance inventory, optimize shelf placement, activate ghost capacity, and prevent picking mistakes.

## Project Structure

```text
backend/
  agents.py
  main.py
frontend/
  app.py
data/
  sample_data.csv
README.md
```

## Requirements

- Python 3.11
- Recommended packages:
  - fastapi
  - uvicorn
  - streamlit
  - requests

Install them with:

```bash
pip install fastapi uvicorn streamlit requests
```

## Run the Backend

Open a terminal in the `backend` directory:

```bash
cd backend
uvicorn main:app --reload
```

The API will start at `http://127.0.0.1:8000`.

## Run the Frontend

Open a second terminal in the `frontend` directory:

```bash
cd frontend
streamlit run app.py
```

The dashboard will open in your browser and use the backend URL `http://127.0.0.1:8000` by default.

## Core Workflow Implemented

1. Demand Agent detects demand surge
2. Store Allocation Agent redirects orders
3. Inventory Agent balances stock
4. Layout Optimization Agent optimizes shelf placement
5. Capacity Agent activates ghost store
6. Error Detection Agent prevents picking mistakes

## API Endpoints

- `POST /predict-demand`
- `POST /allocate-store`
- `POST /balance-inventory`
- `POST /optimize-layout`
- `POST /activate-capacity`
- `POST /check-error`

All endpoints accept JSON input and return structured JSON output.

## Example Inputs

### 1. Predict Demand

```json
{
  "rainfall": 80,
  "festival": true
}
```

### 2. Allocate Store

```json
{
  "store_load": [
    {"store": "Store A", "load": 65},
    {"store": "Store B", "load": 40},
    {"store": "Store C", "load": 30}
  ],
  "distance": {
    "Store A": 2,
    "Store B": 4,
    "Store C": 6
  },
  "inventory": {
    "Store A": 50,
    "Store B": 85,
    "Store C": 60
  }
}
```

### 3. Balance Inventory

```json
{
  "stock_levels": {
    "Store A": 80,
    "Store B": 25,
    "Store C": 50
  }
}
```

### 4. Optimize Layout

```json
{
  "picking_frequency": {
    "Milk": 48,
    "Bread": 40,
    "Chips": 28,
    "Juice": 18
  }
}
```

### 5. Activate Capacity

```json
{
  "demand": 140,
  "capacity": 100
}
```

### 6. Check Error

```json
{
  "expected_item": "Organic Milk",
  "scanned_item": "Organic Milk"
}
```

## Notes

- The app uses simple deterministic rules, not heavy machine learning.
- Data is stored in memory and in a mock CSV file. No external database is required.
- The frontend presents each agent in a separate dashboard section with clear status colors.
