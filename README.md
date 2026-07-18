# banking-ai-agent
"A production-ready, database-driven AI Customer Support Agent for banking products, built with FastAPI, LangChain, and PostgreSQL utilizing Tool Calling architecture."

### 💰 Core Banking Operations
The system supports three core transactional processes with strict validation rules:
* **Deposit:** Safely credits funds to a verified account.
* **Withdrawal:** Debits funds after verifying sufficient balance to prevent overdrafts.
* **Fund Transfer:** Executes a secure transfer between two existing accounts using a robust schema (`TransferTransaction`) that tracks the source, target, and transaction description.