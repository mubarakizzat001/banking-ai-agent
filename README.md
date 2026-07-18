# banking-ai-agent

> A production-ready, database-driven AI Customer Support Agent for banking products, built with **FastAPI**, **LangChain**, and **PostgreSQL** utilizing a Tool Calling architecture.

---

## 🏗️ Project Structure

```
banking-ai-agent/
└── app/
    ├── main.py                  # FastAPI application entry point
    ├── api/
    │   ├── router.py            # Master router (aggregates all sub-routers)
    │   ├── routers/
    │   │   └── Transaction.py   # Endpoints: /deposit, /withdraw, /transfer
    │   └── schema/
    │       ├── Transaction.py         # Request schemas (input validation)
    │       └── TransactionResponse.py # Response schemas (output shaping)
    └── service/
        └── Transaction.py       # Business logic for all transactions
```

---

## 💰 Core Banking Operations

The system supports three core transactional processes with strict validation rules:

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Deposit | `/transactions/deposit` | `POST` |
| Withdrawal | `/transactions/withdraw` | `POST` |
| Fund Transfer | `/transactions/transfer` | `POST` |

* **Deposit:** Safely credits funds to a verified account.
* **Withdrawal:** Debits funds after verifying sufficient balance to prevent overdrafts.
* **Fund Transfer:** Executes a secure transfer between two existing accounts, tracking source, target, and transaction description.

---

## 📦 Schema Design

Schemas are split into two separate files to clearly separate **request** (input) from **response** (output) contracts.

### Request Schemas — `app/api/schema/Transaction.py`

All request schemas inherit from `BaseTransaction` which enforces:
- `amount`: must be `> 0`
- `description`: required, cannot be empty

| Schema | Extra Fields |
|--------|-------------|
| `DepositTransaction` | `account_number` |
| `WithdrawalTransaction` | `account_number` |
| `TransferTransaction` | `source_account_number`, `target_account_number` |

### Response Schemas — `app/api/schema/TransactionResponse.py`

All response schemas inherit from `TransactionResponse` which includes:
- `amount`: the transacted amount
- `description`: transaction description
- `balance`: updated account balance after the operation

| Schema | Extra Fields |
|--------|-------------|
| `DepositTransactionResponse` | `account_number` |
| `WithdrawalTransactionResponse` | `account_number` |
| `TransferTransactionResponse` | `source_account_number`, `target_account_number` |

---

## 🔧 Import Path Convention

Since FastAPI auto-discovers the application from the `app/` directory (adding it to `sys.path`), all internal imports must be written **without** the `app.` prefix:

```python
# ✅ Correct
from service.Transaction import ServiceTransaction
from api.schema.Transaction import DepositTransaction

# ❌ Incorrect — causes ModuleNotFoundError
from app.service.Transaction import ServiceTransaction
from app.api.schema.Transaction import DepositTransaction
```

---

## 🚀 Running the Application

```bash
# 1. Activate the virtual environment
source venv/bin/activate

# 2. Start the development server
fastapi dev
```

The API will be available at:
- **Base URL:** `http://127.0.0.1:8000`
- **Swagger Docs:** `http://127.0.0.1:8000/docs`
- **Scalar Docs:** `http://127.0.0.1:8000/scalar`

---

## 🛡️ Error Handling

The service layer raises appropriate HTTP exceptions:

| Status Code | Condition |
|-------------|-----------|
| `404 Not Found` | Account number does not exist |
| `400 Bad Request` | Insufficient funds for withdrawal or transfer |