# 🏦 Banking AI Agent

> A production-ready, database-driven Banking API built with **FastAPI**, **SQLModel**, **PostgreSQL (asyncpg)**, and **Pydantic v2** — featuring customer management, account lifecycle, and transactional banking operations with a clean service-oriented architecture.

---

## 🏗️ Project Structure

```
banking-ai-agent/
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── app/
    ├── main.py                # FastAPI entry point & lifespan events
    ├── config.py              # Pydantic Settings (DB config from .env)
    ├── api/
    │   ├── router.py          # Master router (aggregates all sub-routers)
    │   ├── dependencies.py    # Dependency injection (session + services)
    │   ├── routers/
    │   │   ├── Customer.py    # POST /customers/customers
    │   │   ├── Account.py     # POST & GET /accounts/accounts
    │   │   └── Transaction.py # POST /transactions/{deposit,withdraw,transfer}
    │   └── schema/
    │       ├── Customer.py          # Customer request/response schemas
    │       ├── account.py           # Account request/response schemas
    │       ├── Transaction.py       # Transaction request schemas
    │       └── TransactionResponse.py  # Transaction response schemas
    ├── database/
    │   ├── models.py          # SQLModel table definitions (Customer, Account, Transaction)
    │   └── session.py         # Async engine, session factory, & table creation
    └── service/
        ├── BaseService.py     # Generic CRUD base (get, create, update, delete)
        ├── CustomerService.py # Customer creation with duplicate checks
        ├── AccountSerivce.py  # Account creation & lookup
        └── Transaction.py     # Deposit, withdrawal, & transfer logic
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ORM / Models | SQLModel (SQLAlchemy + Pydantic) |
| Database | PostgreSQL (async via `asyncpg`) |
| Validation | Pydantic v2 |
| Config | `pydantic-settings` (reads `.env`) |
| API Docs | Swagger UI + Scalar |

---

## 🗄️ Database Models

All models live in `app/database/models.py` and use **SQLModel** with PostgreSQL-specific column types.

### Customer

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | `UUID` | Primary key, auto-generated |
| `name` | `str` | Max 100 chars |
| `email` | `EmailStr` | Max 100 chars, unique |
| `phone` | `str` | Max 15 chars |
| `created_at` | `datetime` | Auto-set on creation |
| `accounts` | `list[Account]` | One-to-many relationship (selectin loading) |

### Account

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | `UUID` | Primary key, auto-generated |
| `customer_id` | `UUID` | Foreign key → `customer.id` |
| `name` | `str` | Inherited from customer name |
| `account_number` | `str` | Auto-generated via DB sequence (starts at `10000000`), unique, indexed |
| `account_type` | `AccountType` | Enum: `savings`, `current`, `salary` |
| `balance` | `float` | Default `0.0` |
| `status` | `str` | Default `ACTIVE` |
| `created_at` | `datetime` | Auto-set on creation |

### Transaction

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | `UUID` | Primary key, auto-generated |
| `account_number` | `str` | Max 20 chars, indexed |
| `amount` | `float` | Required |
| `transaction_type` | `str` | `DEPOSIT`, `WITHDRAWAL`, or `TRANSFER` |
| `created_at` | `datetime` | Auto-set on creation |

---

## 📡 API Endpoints

### Customer

| Operation | Endpoint | Method | Request Schema | Response Schema |
|-----------|----------|--------|----------------|-----------------|
| Create Customer | `/customers/customers` | `POST` | `CustomerCreate` | `CustomerResponse` |

### Account

| Operation | Endpoint | Method | Request Schema | Response Schema |
|-----------|----------|--------|----------------|-----------------|
| Create Account | `/accounts/accounts` | `POST` | `AccountCreate` | `AccountResponse` |
| Get Account | `/accounts/accounts/{account_number}` | `GET` | — | `AccountResponse` |

### Transactions

| Operation | Endpoint | Method | Request Schema | Response Schema |
|-----------|----------|--------|----------------|-----------------|
| Deposit | `/transactions/deposit` | `POST` | `DepositTransaction` | `DepositTransactionResponse` |
| Withdrawal | `/transactions/withdraw` | `POST` | `WithdrawalTransaction` | `WithdrawalTransactionResponse` |
| Fund Transfer | `/transactions/transfer` | `POST` | `TransferTransaction` | `TransferTransactionResponse` |

---

## 📦 Schema Design

### Customer Schemas — `api/schema/Customer.py`

| Schema | Purpose | Fields |
|--------|---------|--------|
| `CustomerBase` | Shared base | `name`, `email`, `phone` |
| `CustomerCreate` | Create request | Inherits `CustomerBase` |
| `CustomerUpdate` | Update request | Inherits `CustomerBase` |
| `CustomerResponse` | API response | Inherits `CustomerBase` + `id` |

### Account Schemas — `api/schema/account.py`

| Schema | Purpose | Fields |
|--------|---------|--------|
| `AccountCreate` | Create request | `customer_id`, `account_type` |
| `AccountResponse` | API response | `account_number`, `account_type`, `name`, `balance`, `status`, `created_at` |

### Transaction Request Schemas — `api/schema/Transaction.py`

All request schemas inherit from `BaseTransaction` which enforces:
- `amount`: must be `> 0`
- `description`: required, cannot be empty

| Schema | Extra Fields |
|--------|-------------|
| `DepositTransaction` | `account_number` |
| `WithdrawalTransaction` | `account_number` |
| `TransferTransaction` | `source_account_number`, `target_account_number` |

### Transaction Response Schemas — `api/schema/TransactionResponse.py`

All response schemas inherit from `TransactionResponse` which includes:
- `amount`, `description`, `balance`

| Schema | Extra Fields |
|--------|-------------|
| `DepositTransactionResponse` | `account_number` |
| `WithdrawalTransactionResponse` | `account_number` |
| `TransferTransactionResponse` | `source_account_number`, `target_account_number` |

---

## 🧩 Architecture Patterns

### Service Layer (`BaseService`)

All services extend `BaseService` which provides generic async CRUD:

```python
class BaseService:
    async def _get(model, id)       # Fetch by primary key
    async def _create(data)         # Insert + commit + refresh
    async def _update(data)         # Upsert + commit + refresh
    async def _delete(data)         # Delete + commit
```

### Dependency Injection (`api/dependencies.py`)

The DI layer wires async DB sessions into services using FastAPI's `Depends`:

```
Request → get_session() → Service(session) → Router
```

Each service has a dedicated factory function and an `Annotated` type alias:

| Dependency | Injected Service |
|------------|-----------------|
| `customerServiceDep` | `CustomerService` |
| `accountServiceDep` | `AccountService` |
| `transactionServiceDep` | `TransactionService` |

---

## 🛡️ Error Handling

The service layer raises appropriate HTTP exceptions:

| Status Code | Condition |
|-------------|-----------|
| `400 Bad Request` | Insufficient balance for withdrawal / transfer |
| `400 Bad Request` | Transfer to the same account |
| `400 Bad Request` | Account is not active |
| `400 Bad Request` | Duplicate email or phone (customer creation) |
| `400 Bad Request` | One or both accounts inactive (transfer) |
| `404 Not Found` | Account number does not exist |
| `404 Not Found` | Customer not found (account creation) |
| `404 Not Found` | Source or destination account not found (transfer) |

---

## 🔧 Import Path Convention

Since FastAPI auto-discovers the application from the `app/` directory (adding it to `sys.path`), all internal imports must be written **without** the `app.` prefix:

```python
# ✅ Correct
from service.Transaction import TransactionService
from database.models import Account, Customer

# ❌ Incorrect — causes ModuleNotFoundError
from app.service.Transaction import TransactionService
from app.database.models import Account, Customer
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (running instance)

### 1. Clone & Install

```bash
git clone <repo-url>
cd banking-ai-agent

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
postgres_server="localhost"
postgres_port=5432
postgres_user="your_user"
postgres_password="your_password"
postgres_db="banking_db"
```

### 3. Run the Application

```bash
cd app
fastapi dev
```

Tables are **auto-created** on startup via the lifespan event.

### 4. Access the API

| Resource | URL |
|----------|-----|
| Base URL | `http://127.0.0.1:8000` |
| Swagger Docs | `http://127.0.0.1:8000/docs` |
| Scalar Docs | `http://127.0.0.1:8000/scalar` |

---

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file.