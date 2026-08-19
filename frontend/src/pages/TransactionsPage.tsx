import { useState, type FormEvent, type ReactElement } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Alert } from "../components/Alert";
import { Field, SelectField } from "../components/Field";
import { useAuth } from "../context/AuthContext";
import { accountsApi, transactionsApi, ApiError } from "../lib/api";
import { ACCOUNT_TYPES, type Account, type AccountType } from "../lib/types";

type Tab = "deposit" | "withdraw" | "transfer" | "send" | "lookup";

const TABS: { id: Tab; label: string }[] = [
  { id: "deposit", label: "Deposit" },
  { id: "withdraw", label: "Withdraw" },
  { id: "transfer", label: "Transfer" },
  { id: "send", label: "Send from my account" },
  { id: "lookup", label: "Look up account" },
];

function useFormResult() {
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function reset() {
    setError(null);
    setSuccess(null);
  }

  async function run(action: () => Promise<string>) {
    reset();
    setLoading(true);
    try {
      setSuccess(await action());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return { error, success, loading, run };
}

function ResultBanner({ error, success }: { error: string | null; success: string | null }) {
  if (error) return <Alert tone="error">{error}</Alert>;
  if (success) return <Alert tone="success">{success}</Alert>;
  return null;
}

function DepositForm() {
  const { error, success, loading, run } = useFormResult();
  const [accountNumber, setAccountNumber] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    run(async () => {
      const result = await transactionsApi.deposit({
        account_number: accountNumber,
        amount: Number(amount),
        description,
      });
      return `Deposited $${result.amount} into ${result.account_number}. New balance: $${result.balance}.`;
    });
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <ResultBanner error={error} success={success} />
      <Field label="Account number" required value={accountNumber} onChange={(e) => setAccountNumber(e.target.value)} />
      <Field label="Amount" type="number" min="0.01" step="0.01" required value={amount} onChange={(e) => setAmount(e.target.value)} />
      <Field label="Description" required value={description} onChange={(e) => setDescription(e.target.value)} />
      <Button type="submit" loading={loading} className="w-full">
        Deposit
      </Button>
    </form>
  );
}

function WithdrawForm() {
  const { error, success, loading, run } = useFormResult();
  const [accountNumber, setAccountNumber] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    run(async () => {
      const result = await transactionsApi.withdraw({
        account_number: accountNumber,
        amount: Number(amount),
        description,
      });
      return `Withdrew $${result.amount} from ${result.account_number}. New balance: $${result.balance}.`;
    });
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <ResultBanner error={error} success={success} />
      <Field label="Account number" required value={accountNumber} onChange={(e) => setAccountNumber(e.target.value)} />
      <Field label="Amount" type="number" min="0.01" step="0.01" required value={amount} onChange={(e) => setAmount(e.target.value)} />
      <Field label="Description" required value={description} onChange={(e) => setDescription(e.target.value)} />
      <Button type="submit" loading={loading} className="w-full">
        Withdraw
      </Button>
    </form>
  );
}

function TransferForm() {
  const { error, success, loading, run } = useFormResult();
  const [source, setSource] = useState("");
  const [target, setTarget] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    run(async () => {
      const result = await transactionsApi.transfer({
        source_account_number: source,
        target_account_number: target,
        amount: Number(amount),
        description,
      });
      return `Transferred $${result.amount} from ${result.source_account_number} to ${result.target_account_number}.`;
    });
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <ResultBanner error={error} success={success} />
      <Field label="Source account number" required value={source} onChange={(e) => setSource(e.target.value)} />
      <Field label="Target account number" required value={target} onChange={(e) => setTarget(e.target.value)} />
      <Field label="Amount" type="number" min="0.01" step="0.01" required value={amount} onChange={(e) => setAmount(e.target.value)} />
      <Field label="Description" required value={description} onChange={(e) => setDescription(e.target.value)} />
      <Button type="submit" loading={loading} className="w-full">
        Transfer
      </Button>
    </form>
  );
}

function SendFromMyAccountForm() {
  const { profile } = useAuth();
  const { error, success, loading, run } = useFormResult();
  const [accountType, setAccountType] = useState<AccountType>("SAVINGS");
  const [target, setTarget] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!profile) return;
    run(async () => {
      const result = await transactionsApi.transferFromMyAccount(
        { target_account: target, account_type: accountType, amount: Number(amount), description },
        profile.token
      );
      return `Sent $${result.amount} from your ${result.account_type} account to ${result.target_account}.`;
    });
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <ResultBanner error={error} success={success} />
      <SelectField
        label="From my account"
        value={accountType}
        onChange={(e) => setAccountType(e.target.value as AccountType)}
      >
        {ACCOUNT_TYPES.map((type) => (
          <option key={type} value={type}>
            {type}
          </option>
        ))}
      </SelectField>
      <Field label="Target account number" required value={target} onChange={(e) => setTarget(e.target.value)} />
      <Field label="Amount" type="number" min="0.01" step="0.01" required value={amount} onChange={(e) => setAmount(e.target.value)} />
      <Field label="Description" required value={description} onChange={(e) => setDescription(e.target.value)} />
      <Button type="submit" loading={loading} className="w-full">
        Send
      </Button>
    </form>
  );
}

function LookupForm() {
  const [accountNumber, setAccountNumber] = useState("");
  const [result, setResult] = useState<Account | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      setResult(await accountsApi.get(accountNumber));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      {error && <Alert tone="error">{error}</Alert>}
      <Field label="Account number" required value={accountNumber} onChange={(e) => setAccountNumber(e.target.value)} />
      <Button type="submit" loading={loading} className="w-full">
        Look up
      </Button>
      {result && (
        <dl className="grid grid-cols-2 gap-3 rounded-xl bg-ink-50 p-4 text-sm">
          <dt className="text-ink-500">Holder</dt>
          <dd className="text-right font-medium text-ink-900">{result.name}</dd>
          <dt className="text-ink-500">Type</dt>
          <dd className="text-right font-medium text-ink-900">{result.account_type}</dd>
          <dt className="text-ink-500">Balance</dt>
          <dd className="text-right font-medium text-ink-900">${result.balance}</dd>
          <dt className="text-ink-500">Status</dt>
          <dd className="text-right font-medium text-ink-900">{result.status}</dd>
        </dl>
      )}
    </form>
  );
}

const TAB_FORMS: Record<Tab, () => ReactElement> = {
  deposit: DepositForm,
  withdraw: WithdrawForm,
  transfer: TransferForm,
  send: SendFromMyAccountForm,
  lookup: LookupForm,
};

export function TransactionsPage() {
  const [tab, setTab] = useState<Tab>("deposit");
  const ActiveForm = TAB_FORMS[tab];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-ink-900">Transactions</h1>
        <p className="mt-1 text-sm text-ink-500">Move money in, out, and between accounts.</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
              tab === t.id ? "bg-brand-600 text-white shadow-soft" : "bg-white text-ink-600 border border-ink-200 hover:bg-ink-50"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <Card className="max-w-md">
        <ActiveForm />
      </Card>
    </div>
  );
}
