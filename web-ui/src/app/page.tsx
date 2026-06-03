"use client";

import { useEffect, useMemo, useState } from "react";
import { BarChart3, CheckCircle2, ClipboardCheck, RefreshCw } from "lucide-react";
import { CameraPanel } from "@/components/CameraPanel";
import { CommandSelector } from "@/components/CommandSelector";
import { PerformancePanel } from "@/components/PerformancePanel";
import { RuleFeedback } from "@/components/RuleFeedback";
import { StatusPill } from "@/components/StatusPill";
import { SummaryCard } from "@/components/SummaryCard";
import { WarningPanel } from "@/components/WarningPanel";
import { fetchEvaluation } from "@/lib/apiClient";
import { getCommand } from "@/lib/commands";
import { createMockEvaluation } from "@/lib/mockEvaluation";
import type { BackendConnectionStatus, CommandId, DrillEvaluation } from "@/types/drill";

export default function DashboardPage() {
  const [selectedCommand, setSelectedCommand] = useState<CommandId>("SAVDHAN");
  const [connectionStatus, setConnectionStatus] = useState<BackendConnectionStatus>("mock");
  const [evaluation, setEvaluation] = useState<DrillEvaluation>(() => createMockEvaluation("SAVDHAN"));
  const [isRefreshing, setIsRefreshing] = useState(false);

  const command = useMemo(() => getCommand(selectedCommand), [selectedCommand]);

  useEffect(() => {
    let isMounted = true;

    async function loadEvaluation() {
      setIsRefreshing(true);
      const result = await fetchEvaluation(selectedCommand);

      if (isMounted) {
        setEvaluation(result.evaluation);
        setConnectionStatus(result.connectionStatus);
        setIsRefreshing(false);
      }
    }

    loadEvaluation();
    const timer = window.setInterval(loadEvaluation, 8000);

    return () => {
      isMounted = false;
      window.clearInterval(timer);
    };
  }, [selectedCommand]);

  const primaryFeed = evaluation.feeds[0];
  const secondaryFeeds = evaluation.feeds.slice(1);
  const scoreLabel = evaluation.overallScore === null ? "--" : `${evaluation.overallScore}%`;
  const backendStatusLabel =
    connectionStatus === "connected" ? "Connected" : connectionStatus === "disconnected" ? "Disconnected" : "Using mock data";

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto flex w-full max-w-[1680px] flex-col gap-5 px-4 py-5 lg:px-6">
        <header className="flex flex-col gap-4 border-b border-white/10 pb-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <StatusPill label={backendStatusLabel} status={connectionStatus} />
              <StatusPill label={evaluation.status.replace("_", " ")} status={evaluation.status} />
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-white md:text-3xl">Drill Evaluation Dashboard</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Modular Next.js control surface for command selection, camera panels, evaluation scores, rule feedback, warnings, and backend telemetry.
            </p>
          </div>

          <button
            onClick={async () => {
              setIsRefreshing(true);
              const result = await fetchEvaluation(selectedCommand);
              setEvaluation(result.evaluation);
              setConnectionStatus(result.connectionStatus);
              setIsRefreshing(false);
            }}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-white/10 bg-white/[0.04] px-4 text-sm font-semibold text-slate-200 transition hover:border-slate-500 hover:bg-white/[0.08]"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </header>

        <div className="grid gap-5 xl:grid-cols-[300px_1fr_320px]">
          <aside className="space-y-5">
            <CommandSelector selectedCommand={selectedCommand} onSelectCommand={setSelectedCommand} />
          </aside>

          <section className="space-y-5">
            <div className="grid gap-4 md:grid-cols-3">
              <SummaryCard icon={ClipboardCheck} label="Selected Command" value={command.code} detail={command.description} />
              <SummaryCard icon={BarChart3} label="Score" value={scoreLabel} detail={evaluation.summary} />
              <SummaryCard icon={CheckCircle2} label="Backend Mode" value={command.backendMode} detail={`${command.rules.length} frontend-visible rules`} emphasis={connectionStatus === "mock"} />
            </div>

            {primaryFeed && <CameraPanel feed={primaryFeed} primary />}

            <div className="grid gap-4 lg:grid-cols-3">
              {secondaryFeeds.map((feed) => (
                <CameraPanel key={feed.id} feed={feed} />
              ))}
            </div>
          </section>

          <aside className="space-y-5">
            <PerformancePanel metrics={evaluation.metrics} />
            <WarningPanel warnings={evaluation.warnings} />
            <RuleFeedback rules={evaluation.rules} />
          </aside>
        </div>
      </div>
    </main>
  );
}
