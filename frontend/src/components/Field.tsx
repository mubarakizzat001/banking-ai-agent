import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes } from "react";

interface FieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

const inputClasses =
  "w-full rounded-xl border border-ink-200 bg-white px-3.5 py-2.5 text-sm text-ink-900 placeholder:text-ink-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100";

export function Field({ label, id, className = "", ...rest }: FieldProps) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");
  return (
    <label htmlFor={inputId} className="block text-left">
      <span className="mb-1.5 block text-sm font-medium text-ink-700">{label}</span>
      <input id={inputId} className={`${inputClasses} ${className}`} {...rest} />
    </label>
  );
}

interface SelectFieldProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  children: ReactNode;
}

export function SelectField({ label, id, className = "", children, ...rest }: SelectFieldProps) {
  const selectId = id ?? label.toLowerCase().replace(/\s+/g, "-");
  return (
    <label htmlFor={selectId} className="block text-left">
      <span className="mb-1.5 block text-sm font-medium text-ink-700">{label}</span>
      <select id={selectId} className={`${inputClasses} ${className}`} {...rest}>
        {children}
      </select>
    </label>
  );
}
