import type { ReactNode } from "react";
import { Card } from "./Card";

export function AuthLayout({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <span className="mx-auto mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-brand-600 text-2xl text-white shadow-soft-lg">
            🏦
          </span>
          <h1 className="text-2xl font-extrabold text-ink-900">{title}</h1>
          <p className="mt-1 text-sm text-ink-500">{subtitle}</p>
        </div>
        <Card>{children}</Card>
      </div>
    </div>
  );
}
