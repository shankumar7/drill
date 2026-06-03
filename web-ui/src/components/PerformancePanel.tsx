import { Activity, Clock3, Gauge, Users } from "lucide-react";
import { MetricCard } from "@/components/MetricCard";
import type { PerformanceMetrics } from "@/types/drill";

interface PerformancePanelProps {
  metrics: PerformanceMetrics;
}

export function PerformancePanel({ metrics }: PerformancePanelProps) {
  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-1">
      <MetricCard icon={Activity} label="Frame Rate" value={`${metrics.fps} fps`} detail="Backend stream performance" />
      <MetricCard icon={Clock3} label="Latency" value={`${metrics.queueLatencyMs} ms`} detail={`${metrics.inferenceMs} ms inference time`} />
      <MetricCard icon={Gauge} label="Dropped Frames" value={`${metrics.droppedFrames}`} detail="Current evaluation window" />
      <MetricCard icon={Users} label="Cadets" value={`${metrics.evaluatedCadets}`} detail="Tracked in latest packet" />
    </div>
  );
}
