import type {
  Account,
  AccountType,
  Customer,
  DepositResult,
  JwtTransferResult,
  TransferResult,
  UserAccount,
  WithdrawalResult,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function extractDetail(data: unknown): string {
  const detail = (data as { detail?: unknown })?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((entry) =>
        typeof entry === "object" && entry && "msg" in entry
          ? String((entry as { msg: unknown }).msg)
          : JSON.stringify(entry)
      )
      .join(", ");
  }
  return JSON.stringify(data);
}

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof URLSearchParams) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, "Could not reach the API. Is the backend running?");
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      detail = extractDetail(await response.json());
    } catch {
      // response had no JSON body
    }
    throw new ApiError(response.status, detail);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const customersApi = {
  create: (data: { name: string; email: string; phone: string }) =>
    request<Customer>("/customers/customers", { method: "POST", body: JSON.stringify(data) }),
};

export const userApi = {
  create: (data: { customer_id: string; password: string }) =>
    request<UserAccount>("/user/create", { method: "POST", body: JSON.stringify(data) }),
  login: (email: string, password: string) =>
    request<{ access_token: string; token_type: string }>("/user/login", {
      method: "POST",
      body: new URLSearchParams({ username: email, password }),
    }),
  logout: (token: string) => request<{ message: string }>("/user/logout", { method: "POST" }, token),
};

export const accountsApi = {
  create: (data: { customer_id: string; account_type: AccountType }) =>
    request<Account>("/accounts/create", { method: "POST", body: JSON.stringify(data) }),
  get: (accountNumber: string) => request<Account>(`/accounts/account/${accountNumber}`),
  myAccount: (accountType: AccountType, token: string) =>
    request<Account>(
      `/accounts/my-accounts?account_type=${accountType}`,
      { method: "POST" },
      token
    ),
  closeMyAccount: (accountType: AccountType, token: string) =>
    request<Account>(
      `/accounts/close-my-account?account_type=${accountType}`,
      { method: "POST" },
      token
    ),
};

export const transactionsApi = {
  deposit: (data: { account_number: string; amount: number; description: string }) =>
    request<DepositResult>("/transactions/deposit", { method: "POST", body: JSON.stringify(data) }),
  withdraw: (data: { account_number: string; amount: number; description: string }) =>
    request<WithdrawalResult>("/transactions/withdraw", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  transfer: (data: {
    source_account_number: string;
    target_account_number: string;
    amount: number;
    description: string;
  }) => request<TransferResult>("/transactions/transfer", { method: "POST", body: JSON.stringify(data) }),
  transferFromMyAccount: (
    data: { target_account: string; account_type: AccountType; amount: number; description: string },
    token: string
  ) =>
    request<JwtTransferResult>(
      "/transactions/transfer_from_my_account",
      { method: "POST", body: JSON.stringify(data) },
      token
    ),
};

export interface ChatStreamEvent {
  event: "token" | "tool_call" | "tool_result" | "error" | "done";
  data: unknown;
}

export async function* streamChat(
  message: string,
  history: { role: "user" | "assistant"; content: string }[],
  token: string,
  signal?: AbortSignal
): AsyncGenerator<ChatStreamEvent> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/agent/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ message, history }),
      signal,
    });
  } catch {
    throw new ApiError(0, "Could not reach the API. Is the backend running?");
  }

  if (!response.ok || !response.body) {
    let detail = response.statusText;
    try {
      detail = extractDetail(await response.json());
    } catch {
      // response had no JSON body
    }
    throw new ApiError(response.status, detail);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let separatorIndex: number;
    while ((separatorIndex = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, separatorIndex);
      buffer = buffer.slice(separatorIndex + 2);

      const eventLine = rawEvent.split("\n").find((line) => line.startsWith("event:"));
      const dataLine = rawEvent.split("\n").find((line) => line.startsWith("data:"));
      if (!eventLine || !dataLine) continue;

      const eventName = eventLine.replace("event:", "").trim() as ChatStreamEvent["event"];
      const dataRaw = dataLine.replace("data:", "").trim();

      if (dataRaw === "[DONE]") {
        yield { event: "done", data: null };
        return;
      }
      try {
        yield { event: eventName, data: JSON.parse(dataRaw) };
      } catch {
        yield { event: eventName, data: dataRaw };
      }
    }
  }
}
