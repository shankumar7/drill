import { AlertTriangle } from "lucide-react";
import type { WarningItem } from "@/types/drill";

interface WarningPanelProps {
  warnings: WarningItem[];
}

const severityStyles: Record<WarningItem["severity"], string> = {
  low: "border-slate-500/20 bg-slate-500/10 text-slate-300",
  medium: "border-amber-500/25 bg-amber-500/10 text-amber-300",
  high: "border-red-500/25 bg-red-500/10 text-red-300",
};

export function WarningPanel({ warnings }: WarningPanelProps) {
  return (
    <section className="panel p-4">
      <div className="mb-4 flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 text-amber-300" />
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-200">Warnings</h2>
      </div>
      <div className="space-y-3">
        {warnings.map((warning) => (
          <div key={warning.id} className={`rounded-md border p-3 ${severityStyles[warning.severity]}`}>
            <div className="text-xs font-semibold uppercase tracking-wide">{warning.severity}</div>
            <p className="mt-1 text-xs leading-5 text-slate-300">{warning.message}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
