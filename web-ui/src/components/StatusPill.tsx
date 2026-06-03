import { AlertTriangle, CheckCircle2, CircleDashed, Wifi, WifiOff } from "lucide-react";
import type { BackendConnectionStatus, EvaluationStatus } from "@/types/drill";

interface StatusPillProps {
  label: string;
  status: EvaluationStatus | BackendConnectionStatus;
}

const statusStyles: Record<string, string> = {
  pass: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  partial_pass: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  needs_attention: "border-red-500/30 bg-red-500/10 text-red-300",
  not_evaluable: "border-slate-500/30 bg-slate-500/10 text-slate-300",
  connected: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  mock: "border-sky-500/30 bg-sky-500/10 text-sky-300",
  disconnected: "border-red-500/30 bg-red-500/10 text-red-300",
};

export function StatusPill({ label, status }: StatusPillProps) {
  const Icon =
    status === "connected" ? Wifi : status === "disconnected" ? WifiOff : status === "pass" ? CheckCircle2 : status === "not_evaluable" ? CircleDashed : AlertTriangle;

  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${statusStyles[status]}`}>
      <Icon className="h-3.5 w-3.5" />
      {label}
    </span>
  );
}
