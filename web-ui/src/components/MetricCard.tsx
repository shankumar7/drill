import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  detail: string;
}

export function MetricCard({ icon: Icon, label, value, detail }: MetricCardProps) {
  return (
    <section className="panel p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</span>
        <Icon className="h-4 w-4 text-slate-500" />
      </div>
      <div className="text-2xl font-semibold text-white">{value}</div>
      <p className="mt-1 text-xs text-slate-500">{detail}</p>
    </section>
  );
}
