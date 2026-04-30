<div align="center">

# 🤖 MALO
### Multi-Agent Autonomous Logistics Orchestrator

*A quick-commerce logistics simulation powered by six rule-based AI agents*

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Overview

MALO simulates the backend intelligence of a modern quick-commerce platform. Six specialized AI agents collaborate to handle demand spikes, store routing, inventory health, shelf layout, overflow capacity, and fulfilment accuracy — all orchestrated through a clean REST API and a live Streamlit dashboard.

> Built as part of the **AI Powered Solutions Expo (Vibeathon)** — April 15, 2026  
> Organized by EDC, IIC, CSE & CSE(AI&ML) at Gopalan College of Engineering and Management, Bengaluru.

---

## 🧠 The Six Agents

| # | Agent | Responsibility |
|---|-------|---------------|
| 1 | 🔍 **Demand Agent** | Detects demand surges using signals like rainfall and festival flags |
| 2 | 🏪 **Store Allocation Agent** | Routes orders to the optimal store based on load, distance & inventory |
| 3 | ⚖️ **Inventory Agent** | Rebalances stock levels across stores to prevent shortfalls |
| 4 | 🗂️ **Layout Optimization Agent** | Reorganizes shelf placement by picking frequency to speed up fulfilment |
| 5 | 👻 **Capacity Agent** | Activates ghost store capacity when demand exceeds available supply |
| 6 | ✅ **Error Detection Agent** | Catches picking mistakes by comparing expected vs. scanned items |

---

## 🗂️ Project Structure

```
MALO/
├── backend/
│   ├── agents.py       # Core agent logic
│   └── main.py         # FastAPI app & route definitions
├── frontend/
│   └── app.py          # Streamlit dashboard
├── data/
│   └── sample_data.csv # Mock dataset
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+

### Install dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install fastapi uvicorn streamlit requests
```

---

## 🚀 Running the App

### 1. Start the Backend

```bash
cd backend
uvicorn main:app --reload
```

API will be live at: `http://127.0.0.1:8000`  
Interactive docs at: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend

Open a second terminal:

```bash
cd frontend
streamlit run app.py
```

The dashboard will open in your browser, connected to the backend by default.

---

## 🔌 API Reference

All endpoints accept and return JSON.

| Method | Endpoint | Agent |
|--------|----------|-------|
| `POST` | `/predict-demand` | Demand Agent |
| `POST` | `/allocate-store` | Store Allocation Agent |
| `POST` | `/balance-inventory` | Inventory Agent |
| `POST` | `/optimize-layout` | Layout Optimization Agent |
| `POST` | `/activate-capacity` | Capacity Agent |
| `POST` | `/check-error` | Error Detection Agent |

### Example Requests

<details>
<summary><strong>POST /predict-demand</strong></summary>

```json
{
  "rainfall": 80,
  "festival": true
}
```
</details>

<details>
<summary><strong>POST /allocate-store</strong></summary>

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
</details>

<details>
<summary><strong>POST /balance-inventory</strong></summary>

```json
{
  "stock_levels": {
    "Store A": 80,
    "Store B": 25,
    "Store C": 50
  }
}
```
</details>

<details>
<summary><strong>POST /optimize-layout</strong></summary>

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
</details>

<details>
<summary><strong>POST /activate-capacity</strong></summary>

```json
{
  "demand": 140,
  "capacity": 100
}
```
</details>

<details>
<summary><strong>POST /check-error</strong></summary>

```json
{
  "expected_item": "Organic Milk",
  "scanned_item": "Organic Milk"
}
```
</details>

---

## 🏗️ Design Decisions

- **Rule-based agents over ML** — keeps the system fast, transparent, and easy to debug. No training data or model files required.
- **In-memory + CSV storage** — zero infrastructure dependencies. Clone and run.
- **Decoupled frontend/backend** — the Streamlit dashboard communicates via REST, so the backend can be swapped or extended independently.

---

## 🛣️ Future Improvements

- [ ] Add ML-based demand forecasting (e.g. XGBoost / time-series models)
- [ ] Persistent database (PostgreSQL or SQLite)
- [ ] Agent-to-agent communication via message queue
- [ ] Docker Compose setup for one-command deployment
- [ ] Unit tests for each agent

---

## 👥 Team

Built with ❤️ at **Vibeathon 2026**

- **Anup Kumar Jena** — [GitHub](https://github.com/AKJenaX)
- Teammate 1
- Teammate 2

---

## 📄 License

This project is open source under the [MIT License](LICENSE).
