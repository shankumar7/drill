export type CommandId =
  | "SAVDHAN"
  | "VISHRAM"
  | "LO_1_1_2"
  | "LO_1_1_3"
  | "LO_1_1_4"
  | "LO_1_1_5"
  | "LO_1_1_6"
  | "LO_1_1_7"
  | "LO_1_1_8"
  | "LO_1_1_9"
  | "LO_1_1_10"
  | "LO_1_1_11";

export type EvaluationStatus = "pass" | "partial_pass" | "needs_attention" | "not_evaluable";

export type BackendConnectionStatus = "connected" | "disconnected" | "mock";

export interface DrillCommand {
  id: CommandId;
  code: string;
  label: string;
  category: "Core Posture" | "LO 1.1 Series";
  group: "Core Commands" | "LO 1.1";
  description: string;
  expectedDurationSec: number;
  backendMode: string;
  rules: string[];
}

export interface RuleResult {
  name: string;
  status: EvaluationStatus;
  score: number | null;
  message: string;
}

export interface PerformanceMetrics {
  fps: number;
  inferenceMs: number;
  queueLatencyMs: number;
  droppedFrames: number;
  evaluatedCadets: number;
}

export interface WarningItem {
  id: string;
  severity: "low" | "medium" | "high";
  message: string;
}

export interface FeedSource {
  id: string;
  label: string;
  perspective: string;
  endpoint: string;
  status: "live" | "standby" | "unavailable";
}

export interface DrillEvaluation {
  commandId: CommandId;
  mode: string;
  overallScore: number | null;
  status: EvaluationStatus;
  summary: string;
  rules: RuleResult[];
  warnings: WarningItem[];
  metrics: PerformanceMetrics;
  feeds: FeedSource[];
  updatedAt: string;
}
