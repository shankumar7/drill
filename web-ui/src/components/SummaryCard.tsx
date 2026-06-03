import type { LucideIcon } from "lucide-react";

interface SummaryCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  detail: string;
  emphasis?: boolean;
}

export function SummaryCard({ icon: Icon, label, value, detail, emphasis = false }: SummaryCardProps) {
  return (
    <section className={`panel p-4 ${emphasis ? "border-sky-400/40 bg-sky-500/10" : ""}`}>
      <div className="mb-3 flex items-center justify-between gap-3">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</span>
        <Icon className="h-4 w-4 text-sky-300" />
      </div>
      <div className="text-2xl font-semibold text-white">{value}</div>
      <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">{detail}</p>
    </section>
  );
}
