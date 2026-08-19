import type { ReactNode } from "react";

type Tone = "error" | "success" | "info";

const TONE_CLASSES: Record<Tone, string> = {
  error: "bg-danger-50 text-danger-700 border-danger-100",
  success: "bg-success-50 text-success-700 border-success-100",
  info: "bg-brand-50 text-brand-700 border-brand-100",
};

export function Alert({ tone = "info", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <div className={`rounded-xl border px-4 py-3 text-sm ${TONE_CLASSES[tone]}`} role="status">
      {children}
    </div>
  );
}
