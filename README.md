# 🏦 Banking AI Agent

> A database-driven Banking API built with **FastAPI**, **SQLModel**, **PostgreSQL (asyncpg)**, **Redis**, and **Pydantic v2** — featuring customer management, JWT authentication, account lifecycle, and transactional banking operations with a clean service-oriented architecture.

> 🚧 **Status: Active development.** The core banking + auth flow is implemented, but this project is not finished. See [Roadmap](#-roadmap) for what's planned next, including an AI-powered customer support agent.

---

## 🧪 Public "Sandbox" Endpoints vs. Customer-Protected Endpoints

[#-public-sandbox-endpoints-vs-customer-protected-endpoints](#-public-sandbox-endpoints-vs-customer-protected-endpoints)

This project intentionally exposes **two layers** of endpoints:

- **Sandbox layer (no auth required)** — `POST /customers/customers`, `POST /accounts/create`, `GET /accounts/account/{account_number}`, `POST /transactions/deposit`, `/withdraw`, `/transfer`. These exist so anyone cloning the repo can create test customers/accounts and try deposits, withdrawals, and transfers immediately, without first wiring up a login flow. Think of it as a public playground for exploring the API.
- **Customer layer (JWT-protected)** — everything under an authenticated session: `POST /user/login`, `GET /accounts/my-accounts`, `POST /accounts/close-my-account`, `POST /transactions/transfer_from_my_account`. This is the real "logged-in customer" experience — the source account is always resolved from the JWT, never taken as raw input, so a customer can only ever move money out of their *own* account.

⚠️ **This split is a deliberate demo/learning-project decision, not an oversight.** In a real production deployment, the sandbox layer would either be removed entirely or placed behind admin-only authentication, and all money-movement would go exclusively through the JWT-protected, customer-scoped routes.

---

## 🏗️ Project Structure

```
banking-ai-agent/
├── .env.example                    # Environment variables template
├── requirements.txt                # Python dependencies
└── app/
    ├── main.py                     # FastAPI entry point & lifespan events
    ├── config.py                   # Pydantic Settings (DB, JWT, Redis config from .env)
    ├── utils.py                    # JWT access token creation & decoding
    ├── api/
    │   ├── router.py                # Master router (aggregates all sub-routers)
    │   ├── dependencies.py          # Dependency injection (session, services, auth)
    │   ├── routers/
    │   │   ├── User.py              # POST /user/create, GET /user/get/{email},
    │   │   │                        # POST /user/login, POST /user/logout
    │   │   ├── Customer.py          # POST /customers/customers
    │   │   ├── Account.py           # POST/GET account endpoints (incl. JWT-protected)
    │   │   └── Transaction.py       # Deposit / withdraw / transfer endpoints
    │   └── schema/
    │       ├── User.py               # User (auth) request/response schemas
    │       ├── Customer.py           # Customer request/response schemas
    │       ├── account.py            # Account request/response schemas
    │       ├── Transaction.py        # Transaction request schemas
    │       └── TransactionResponse.py # Transaction response schemas
    ├── core/
    │   └── security.py              # OAuth2PasswordBearer scheme (tokenUrl=/user/login)
    ├── database/
    │   ├── models.py                # SQLModel tables: Customer, Account, Transaction, UserAccounts
    │   ├── session.py                # Async engine, session factory, & table creation
    │   └── redis.py                  # JWT blacklist (logout) backed by Redis
    └── service/
        ├── BaseService.py            # Generic async CRUD base (get, create, update, delete)
        ├── CustomerService.py        # Customer creation with duplicate checks
        ├── UserService.py            # User registration, login, password hashing
        ├── AccountSerivce.py         # Account creation, lookup, my-accounts, close-account
        └── Transaction.py            # Deposit, withdrawal, transfer & JWT transfer logic
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ORM / Models | SQLModel (SQLAlchemy + Pydantic) |
| Database | PostgreSQL (async via `asyncpg`) |
| Cache / Token Store | Redis (async client, used for JWT blacklisting) |
| Auth | OAuth2 Password Flow + JWT (`PyJWT`) + `bcrypt` password hashing |
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
| `user_accounts` | `list[UserAccounts]` | One-to-one login credentials (selectin loading) |

### Account

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | `UUID` | Primary key, auto-generated |
| `customer_id` | `UUID` | Foreign key → `customer.id` |
| `name` | `str` | Inherited from customer name |
| `account_number` | `str` | Auto-generated via DB sequence (starts at `10000000`), unique, indexed |
| `account_type` | `AccountType` | Enum: `SAVINGS`, `CURRENT`, `SALARY` |
| `balance` | `float` | Default `0.0` |
| `status` | `str` | Default `ACTIVE` (set to `closed` on account closure) |
| `created_at` | `datetime` | Auto-set on creation |

### Transaction

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | `UUID` | Primary key, auto-generated |
| `account_number` | `str` | Max 20 chars, indexed |
| `amount` | `float` | Required |
| `transaction_type` | `str` | `deposit`, `withdrawal`, or `transfer` |
| `created_at` | `datetime` | Auto-set on creation |

### UserAccounts (login credentials)

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | `UUID` | Primary key, auto-generated |
| `customer_id` | `UUID` | Foreign key → `customer.id`, unique (one login per customer) |
| `hash_password` | `str` | Max 256 chars, `bcrypt`-hashed |

---

## 🔐 Authentication & Security

Auth uses the OAuth2 Password flow to issue a JWT that identifies the authenticated `Customer`.

- **Registration** — `UserAccounts` links a `customer_id` to a `bcrypt`-hashed password.
- **Login** — `POST /user/login` verifies credentials and returns a JWT access token containing `customer_id`, an expiry (`exp`, default 2 hours), and a unique token id (`jti`).
- **Authorization** — protected endpoints depend on `get_access_token` (decodes & validates the JWT, rejects blacklisted tokens) and `get_current_user` (resolves the JWT to a `Customer` row).
- **Logout** — `POST /user/logout` adds the token's `jti` to a Redis-backed blacklist (`app/database/redis.py`), so the token is rejected on any subsequent request even though it hasn't expired yet.

| Dependency | Purpose |
|------------|---------|
| `get_access_token` | Decodes the JWT and checks the Redis blacklist |
| `get_current_user` | Resolves the token to the current `Customer` |
| `activeuserdep` | `Annotated[Customer, Depends(get_current_user)]` — use on any route that must act as "the logged-in customer" |

---

## 📡 API Endpoints

### User (Auth)

| Operation | Endpoint | Method | Auth | Request Schema | Response Schema |
|-----------|----------|--------|------|----------------|-----------------|
| Register user | `/user/create` | `POST` | — | `UserCreate` | `UserResponse` |
| Get user by email | `/user/get/{email}` | `GET` | — | — | `UserResponse` |
| Login | `/user/login` | `POST` | — | `OAuth2PasswordRequestForm` (form: `username`, `password`) | `{ access_token, token_type }` |
| Logout | `/user/logout` | `POST` | Bearer token | — | `{ message }` |

### Customer

| Operation | Endpoint | Method | Auth | Request Schema | Response Schema |
|-----------|----------|--------|------|----------------|-----------------|
| Create Customer | `/customers/customers` | `POST` | — | `CustomerCreate` | `CustomerResponse` |

### Account

| Operation | Endpoint | Method | Auth | Request Schema | Response Schema |
|-----------|----------|--------|------|----------------|-----------------|
| Create Account | `/accounts/create` | `POST` | — | `AccountCreate` | `AccountResponse` |
| Get Account | `/accounts/account/{account_number}` | `GET` | — | — | `AccountResponse` |
| My Accounts | `/accounts/my-accounts` | `POST` | Bearer token | query: `account_type` | `MyAccountResponse` |
| Close My Account | `/accounts/close-my-account` | `POST` | Bearer token | query: `account_type` | `AccountResponse` |

### Transactions

| Operation | Endpoint | Method | Auth | Request Schema | Response Schema |
|-----------|----------|--------|------|----------------|-----------------|
| Deposit | `/transactions/deposit` | `POST` | — | `DepositTransaction` | `DepositTransactionResponse` |
| Withdrawal | `/transactions/withdraw` | `POST` | — | `WithdrawalTransaction` | `WithdrawalTransactionResponse` |
| Fund Transfer | `/transactions/transfer` | `POST` | — | `TransferTransaction` | `TransferTransactionResponse` |
| Transfer from my account | `/transactions/transfer_from_my_account` | `POST` | Bearer token | `JWTTransaction` | `JWTTransactionResponse` |

`transfer_from_my_account` resolves the *source* account from the authenticated customer's `account_type` (no need to pass a source account number) and transfers to `target_account`.

---

## 📦 Schema Design

### User Schemas — `api/schema/User.py`

| Schema | Purpose | Fields |
|--------|---------|--------|
| `UserCreate` | Register request | `password`, `customer_id` |
| `UserResponse` | API response | `id`, `customer_id` |
| `UserLogin` | Email/password login payload | `email`, `password` |
| `UserUpdate` | Update request | `email`, `password` |

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
| `MyAccountResponse` | Own-account response (no timestamp) | `account_number`, `account_type`, `name`, `balance`, `status` |

### Transaction Request Schemas — `api/schema/Transaction.py`

All request schemas inherit from `BaseTransaction`, which enforces:
- `amount`: must be `> 0`
- `description`: required, cannot be empty

| Schema | Extra Fields |
|--------|-------------|
| `DepositTransaction` | `account_number` |
| `WithdrawalTransaction` | `account_number` |
| `TransferTransaction` | `source_account_number`, `target_account_number` |
| `JWTTransaction` | `target_account`, `account_type` (source is inferred from the JWT) |

### Transaction Response Schemas — `api/schema/TransactionResponse.py`

All response schemas inherit from `TransactionResponse`, which includes `amount`, `description`.

| Schema | Extra Fields |
|--------|-------------|
| `DepositTransactionResponse` | `account_number`, `balance` |
| `WithdrawalTransactionResponse` | `account_number`, `balance` |
| `TransferTransactionResponse` | `source_account_number`, `target_account_number` |
| `JWTTransactionResponse` | `target_account`, `account_type` |

---

## 🧩 Architecture Patterns

### Service Layer (`BaseService`)

All services extend `BaseService`, which provides generic async CRUD:

```python
class BaseService:
    async def _get(model, id)       # Fetch by primary key
    async def _create(data)         # Insert + commit + refresh
    async def _update(data)         # Upsert + commit + refresh
    async def _delete(data)         # Delete + commit
```

### Dependency Injection (`api/dependencies.py`)

The DI layer wires async DB sessions, Redis-backed auth, and services using FastAPI's `Depends`:

```
Request → get_session() → Service(session) → Router
Request → oauth2_scheme → get_access_token() → get_current_user() → activeuserdep → Router
```

Each service has a dedicated factory function and an `Annotated` type alias:

| Dependency | Injected Service |
|------------|-----------------|
| `customerServiceDep` | `CustomerService` |
| `accountServiceDep` | `AccountService` |
| `transactionServiceDep` | `TransactionService` |
| `userServiceDep` | `UserService` |
| `activeuserdep` | Current authenticated `Customer` |

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
| `400 Bad Request` | Closing an account that isn't active or has a nonzero balance |
| `401 Unauthorized` | Invalid credentials on login |
| `401 Unauthorized` | Missing, invalid, expired, or blacklisted JWT |
| `404 Not Found` | Account number does not exist |
| `404 Not Found` | Customer not found (account/user creation) |
| `404 Not Found` | Source or destination account not found (transfer) |
| `404 Not Found` | User not found (login/get-by-email) |

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
- Redis (running instance, used for JWT blacklisting on logout)

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

Edit `.env` with your PostgreSQL, JWT, and Redis settings (see `app/config.py`):

```env
# PostgreSQL
postgres_server=localhost
postgres_port=5432
postgres_user=your_user
postgres_password=your_password
postgres_db=banking_db

# JWT
jwt_secret=your_jwt_secret
jwt_algorithm=HS256

# Redis
redis_host=localhost
redis_port=6379
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

## 🗺️ Roadmap

This project is still under active development. Planned/upcoming work includes:

- 🤖 **AI Customer Support** — an AI agent to handle customer banking queries (balances, transaction history, general support) on top of the existing services.
- Additional account & transaction management endpoints.
- Broader test coverage.

---

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file.