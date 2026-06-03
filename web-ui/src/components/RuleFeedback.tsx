import { AlertTriangle, CheckCircle2, CircleDashed } from "lucide-react";
import type { RuleResult } from "@/types/drill";

interface RuleFeedbackProps {
  rules: RuleResult[];
}

export function RuleFeedback({ rules }: RuleFeedbackProps) {
  const evaluableRules = rules.filter((rule) => rule.status !== "not_evaluable");
  const notEvaluableRules = rules.filter((rule) => rule.status === "not_evaluable");

  return (
    <section className="panel p-4">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-200">Rule-wise Feedback</h2>
      <RuleList rules={evaluableRules} />

      {notEvaluableRules.length > 0 && (
        <div className="mt-4 border-t border-white/10 pt-4">
          <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Not Evaluable</div>
          <RuleList rules={notEvaluableRules} />
        </div>
      )}
    </section>
  );
}

function RuleList({ rules }: { rules: RuleResult[] }) {
  return (
    <div className="space-y-3">
      {rules.map((rule) => {
        const Icon = rule.status === "pass" ? CheckCircle2 : rule.status === "not_evaluable" ? CircleDashed : AlertTriangle;
        const color = rule.status === "pass" ? "text-emerald-300" : rule.status === "partial_pass" ? "text-amber-300" : rule.status === "not_evaluable" ? "text-slate-400" : "text-red-300";
        const border = rule.status === "needs_attention" ? "border-red-500/25" : rule.status === "not_evaluable" ? "border-slate-500/20" : "border-white/10";

        return (
          <div key={rule.name} className={`rounded-md border ${border} bg-white/[0.03] p-3`}>
            <div className="flex items-start justify-between gap-3">
              <div className="flex gap-3">
                <Icon className={`mt-0.5 h-4 w-4 ${color}`} />
                <div>
                  <h3 className="text-sm font-semibold text-slate-100">{rule.name}</h3>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{rule.message}</p>
                </div>
              </div>
              <span className="font-mono text-sm text-slate-300">{rule.score ?? "--"}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
