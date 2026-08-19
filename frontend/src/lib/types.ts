export type AccountType = "SAVINGS" | "CURRENT" | "SALARY";

export const ACCOUNT_TYPES: AccountType[] = ["SAVINGS", "CURRENT", "SALARY"];

export interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
}

export interface UserAccount {
  id: string;
  customer_id: string;
}

export interface Account {
  account_number: string;
  account_type: AccountType;
  name: string;
  balance: number;
  status: string;
  created_at?: string;
}

export interface DepositResult {
  amount: number;
  description: string;
  account_number: string;
  balance: number;
}

export interface WithdrawalResult {
  amount: number;
  description: string;
  account_number: string;
  balance: number;
}

export interface TransferResult {
  amount: number;
  description: string;
  source_account_number: string;
  target_account_number: string;
}

export interface JwtTransferResult {
  amount: number;
  description: string;
  target_account: string;
  account_type: AccountType;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface JwtPayload {
  user: { id: string; customer_id: string };
  exp: number;
  jti: string;
}
