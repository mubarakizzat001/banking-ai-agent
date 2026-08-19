import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Alert } from "../components/Alert";
import { useAuth } from "../context/AuthContext";
import { accountsApi, ApiError } from "../lib/api";
import { ACCOUNT_TYPES, type Account, type AccountType } from "../lib/types";

type AccountSlot =
  | { status: "loading" }
  | { status: "none" }
  | { status: "ready"; account: Account };

const ACCOUNT_ICON: Record<AccountType, string> = {
  SAVINGS: "🐷",
  CURRENT: "💳",
  SALARY: "💼",
};

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(amount);
}

export function DashboardPage() {
  const { profile } = useAuth();
  const [accounts, setAccounts] = useState<Record<AccountType, AccountSlot>>({
    SAVINGS: { status: "loading" },
    CURRENT: { status: "loading" },
    SALARY: { status: "loading" },
  });
  const [busy, setBusy] = useState<AccountType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const loadAccount = useCallback(
    async (type: AccountType) => {
      if (!profile) return;
      try {
        const account = await accountsApi.myAccount(type, profile.token);
        setAccounts((prev) => ({ ...prev, [type]: { status: "ready", account } }));
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          setAccounts((prev) => ({ ...prev, [type]: { status: "none" } }));
        } else {
          throw err;
        }
      }
    },
    [profile]
  );

  const loadAll = useCallback(async () => {
    setError(null);
    try {
      await Promise.all(ACCOUNT_TYPES.map(loadAccount));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load your accounts.");
    }
  }, [loadAccount]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  if (!profile) return null;

  async function openAccount(type: AccountType) {
    setError(null);
    setBusy(type);
    try {
      await accountsApi.create({ customer_id: profile!.customerId, account_type: type });
      await loadAccount(type);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not open the account.");
    } finally {
      setBusy(null);
    }
  }

  async function closeAccount(type: AccountType) {
    setError(null);
    setBusy(type);
    try {
      await accountsApi.closeMyAccount(type, profile!.token);
      await loadAccount(type);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not close the account.");
    } finally {
      setBusy(null);
    }
  }

  function copyAccountNumber(accountNumber: string) {
    navigator.clipboard?.writeText(accountNumber);
    setCopied(accountNumber);
    setTimeout(() => setCopied(null), 1500);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-ink-900">
          Welcome{profile.name ? `, ${profile.name}` : ""}
        </h1>
        <p className="mt-1 text-sm text-ink-500">Here's an overview of your accounts.</p>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {ACCOUNT_TYPES.map((type) => {
          const slot = accounts[type];
          return (
            <Card key={type} className="flex flex-col justify-between">
              <div className="mb-4 flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-xl bg-brand-50 text-lg">
                  {ACCOUNT_ICON[type]}
                </span>
                <div>
                  <p className="text-sm font-semibold text-ink-900">{type}</p>
                  {slot.status === "ready" && (
                    <p
                      className={`text-xs font-medium ${
                        slot.account.status === "ACTIVE" ? "text-success-600" : "text-ink-400"
                      }`}
                    >
                      {slot.account.status}
                    </p>
                  )}
                </div>
              </div>

              {slot.status === "loading" && (
                <div className="h-16 animate-pulse rounded-xl bg-ink-100" />
              )}

              {slot.status === "none" && (
                <div className="flex flex-1 flex-col justify-between gap-4">
                  <p className="text-sm text-ink-500">You don't have a {type.toLowerCase()} account yet.</p>
                  <Button
                    variant="secondary"
                    onClick={() => openAccount(type)}
                    loading={busy === type}
                    className="w-full"
                  >
                    Open {type.toLowerCase()} account
                  </Button>
                </div>
              )}

              {slot.status === "ready" && (
                <div className="space-y-3">
                  <p className="text-3xl font-extrabold text-ink-900">
                    {formatCurrency(slot.account.balance)}
                  </p>
                  <button
                    onClick={() => copyAccountNumber(slot.account.account_number)}
                    className="flex items-center gap-1.5 rounded-lg bg-ink-50 px-2.5 py-1.5 font-mono text-xs text-ink-600 hover:bg-ink-100"
                    title="Copy account number"
                  >
                    #{slot.account.account_number}
                    <span className="text-ink-400">{copied === slot.account.account_number ? "✓ copied" : "copy"}</span>
                  </button>
                  {slot.account.status === "ACTIVE" && slot.account.balance === 0 && (
                    <Button
                      variant="danger"
                      onClick={() => closeAccount(type)}
                      loading={busy === type}
                      className="w-full"
                    >
                      Close account
                    </Button>
                  )}
                </div>
              )}
            </Card>
          );
        })}
      </div>

      <Card className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="font-semibold text-ink-900">Ready to move money?</p>
          <p className="text-sm text-ink-500">Deposit, withdraw, or transfer between accounts.</p>
        </div>
        <Link to="/transactions">
          <Button>Go to transactions</Button>
        </Link>
      </Card>
    </div>
  );
}
