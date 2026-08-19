import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

export function Card({ children, className = "", ...rest }: CardProps) {
  return (
    <div
      {...rest}
      className={`rounded-2xl border border-ink-100 bg-white p-6 shadow-soft ${className}`}
    >
      {children}
    </div>
  );
}
