"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import { Gauge } from "../components/Gauge";
import { Mic, CheckCircle2, AlertCircle, HelpCircle, ChevronRightCircle, Activity, Camera, Maximize, PlayCircle, Settings, X, LogOut, Check, Wifi, WifiOff, Crosshair, Target, BarChart3 } from "lucide-react";
import { RegistrationScreen } from "./components/RegistrationScreen";
import { motion, AnimatePresence } from "framer-motion";

// ─── Types ───────────────────────────────────────────────────
type CameraMapping = { front: number; side: number; back: number; };

type AppSettings = {
  confidence: number; image_size: number; keypoint_visibility_threshold: number;
  max_detections: number; stale_detection_timeout: number; prefer_half_precision: boolean;
  tracking_config: string; evaluation_fps: number;
  pass_threshold: number; score_smoothing_window: number;
  savdhan_threshold: number; vishram_threshold: number;
  salute_threshold: number; aaram_se_threshold: number;
  voice_enabled: boolean; voice_language: string; voice_initial_prompt: string;
  show_skeleton: boolean; show_id_overlay: boolean; show_confidence_score: boolean;
  skeleton_color: string; overlay_opacity: number; camera_label_position: string;
  auto_save_session: boolean; unit_name: string; instructor_name: string;
  export_format: string; session_duration_limit: number;
  camera_flip_horizontal: boolean; camera_flip_vertical: boolean; camera_fps_cap: number;
  alert_on_pass: boolean; alert_on_fail: boolean; alert_visual_flash: boolean;
  ws_reconnect_interval: number; backend_host: string; backend_port: number;
  side_camera_position: string;
};

const DEFAULT_SETTINGS: AppSettings = {
  confidence: 0.5, image_size: 640, keypoint_visibility_threshold: 0.3,
  max_detections: 10, stale_detection_timeout: 2.0, prefer_half_precision: true,
  tracking_config: "bytetrack.yaml", evaluation_fps: 20,
  pass_threshold: 85, score_smoothing_window: 1,
  savdhan_threshold: 85, vishram_threshold: 80, salute_threshold: 80, aaram_se_threshold: 75,
  voice_enabled: true, voice_language: "en", voice_initial_prompt: "Military drill commands: savadhan, attention, vishram, ease, salute.",
  show_skeleton: true, show_id_overlay: true, show_confidence_score: false,
  skeleton_color: "green", overlay_opacity: 0.8, camera_label_position: "top-left",
  auto_save_session: false, unit_name: "", instructor_name: "Lt Col K Srinath",
  export_format: "json", session_duration_limit: 0,
  camera_flip_horizontal: false, camera_flip_vertical: false, camera_fps_cap: 30,
  alert_on_pass: false, alert_on_fail: true, alert_visual_flash: true,
  side_camera_position: "right",
  ws_reconnect_interval: 3, backend_host: "localhost", backend_port: 8000,
};

// ─── Live Clock ───────────────────────────────────────────────
function LiveClock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => { const t = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(t); }, []);
  return (
    <div className="flex flex-col items-end">
      <span className="text-xs font-mono font-bold text-stone-200 tracking-widest tabular-nums">
        {time.toLocaleTimeString("en-IN", { hour12: false })}
      </span>
      <span className="text-[9px] font-mono text-stone-600 tracking-widest">
        {time.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
      </span>
    </div>
  );
}

// ─── Session Timer ────────────────────────────────────────────
function SessionTimer({ running }: { running: boolean }) {
  const [secs, setSecs] = useState(0);
  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setSecs(s => s + 1), 1000);
    return () => clearInterval(t);
  }, [running]);
  const h = Math.floor(secs / 3600), m = Math.floor((secs % 3600) / 60), s = secs % 60;
  return (
    <div className="flex flex-col items-center">
      <span className="text-[9px] font-black text-stone-600 uppercase tracking-widest mb-0.5">Session</span>
      <span className="text-xs font-mono font-bold text-stone-300 tabular-nums">
        {String(h).padStart(2,"0")}:{String(m).padStart(2,"0")}:{String(s).padStart(2,"0")}
      </span>
    </div>
  );
}

// ─── Settings Modal ───────────────────────────────────────────
type SettingsTab = "camera" | "ai" | "evaluation" | "voice" | "display" | "session" | "network";

function SettingsModal({ isOpen, onClose, mapping, onSave, baseUrl }: {
  isOpen: boolean; onClose: () => void; mapping: CameraMapping;
  onSave: (m: CameraMapping) => void; baseUrl: string;
}) {
  const [activeTab, setActiveTab] = useState<SettingsTab>("camera");
  const [localMap, setLocalMap] = useState<CameraMapping>(mapping);
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");

  useEffect(() => {
    if (!isOpen) return;
    setLocalMap(mapping);
    fetch(`${baseUrl}/api/settings`).then(r => r.json()).then(data => {
      setSettings(s => ({ ...s, ...data }));
    }).catch(() => {});
  }, [isOpen, mapping, baseUrl]);

  const set = <K extends keyof AppSettings>(key: K, val: AppSettings[K]) =>
    setSettings(s => ({ ...s, [key]: val }));

  const handleSave = async () => {
    setSaveStatus("saving");
    try {
      await fetch(`${baseUrl}/api/settings`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...settings, camera_mapping: localMap }),
      });
      onSave(localMap);
      setSaveStatus("saved");
      setTimeout(() => { setSaveStatus("idle"); onClose(); }, 800);
    } catch { setSaveStatus("error"); setTimeout(() => setSaveStatus("idle"), 2000); }
  };

  const handleReset = async () => {
    try { await fetch(`${baseUrl}/api/settings/reset`); setSettings(DEFAULT_SETTINGS); } catch {}
  };

  if (!isOpen) return null;

  const tabs: { id: SettingsTab; label: string }[] = [
    { id: "camera",     label: "Camera" },
    { id: "ai",         label: "AI Engine" },
    { id: "evaluation", label: "Scoring" },
    { id: "voice",      label: "Voice" },
    { id: "display",    label: "Display" },
    { id: "session",    label: "Session" },
    { id: "network",    label: "Network" },
  ];

  const Section = ({ title }: { title: string }) => (
    <div className="text-[9px] font-black tracking-[0.25em] text-stone-600 uppercase mb-3 mt-5 first:mt-0 pb-1 border-b border-white/[0.04]">{title}</div>
  );

  const SliderRow = ({ label, desc, min, max, step, value, unit = "", onChange }: {
    label: string; desc: string; min: number; max: number; step: number; value: number; unit?: string; onChange: (v: number) => void;
  }) => (
    <div className="mb-5">
      <div className="flex justify-between items-center mb-0.5">
        <label className="text-xs font-bold text-stone-300 uppercase tracking-widest">{label}</label>
        <span className="text-xs font-mono text-stone-200 bg-stone-800 border border-white/[0.06] px-2.5 py-0.5 rounded-full min-w-[52px] text-center">{value}{unit}</span>
      </div>
      <p className="text-[10px] text-stone-600 mb-2 leading-relaxed">{desc}</p>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="w-full h-1 bg-stone-700 rounded-full appearance-none cursor-pointer accent-stone-300" />
      <div className="flex justify-between text-[9px] text-stone-700 mt-1 font-mono"><span>{min}{unit}</span><span>{max}{unit}</span></div>
    </div>
  );

  const ToggleRow = ({ label, desc, value, onChange, badge }: {
    label: string; desc: string; value: boolean; onChange: (v: boolean) => void; badge?: string;
  }) => (
    <div className="flex items-center justify-between mb-3 p-3.5 bg-stone-800/40 rounded-xl border border-white/[0.05] hover:border-white/10 transition-colors group">
      <div className="flex-1 mr-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-stone-200 uppercase tracking-widest">{label}</span>
          {badge && <span className="text-[8px] font-black px-1.5 py-0.5 bg-stone-700 text-stone-500 rounded uppercase tracking-wider">{badge}</span>}
        </div>
        <div className="text-[10px] text-stone-600 mt-0.5 leading-relaxed">{desc}</div>
      </div>
      <button onClick={() => onChange(!value)} className={`relative w-11 h-6 rounded-full transition-all shrink-0 ${value ? "bg-stone-300" : "bg-stone-700 group-hover:bg-stone-600"}`}>
        <span className={`absolute top-1 w-4 h-4 rounded-full bg-stone-950 shadow transition-all duration-200 ${value ? "left-6" : "left-1"}`} />
      </button>
    </div>
  );

  const SelectRow = ({ label, desc, value, options, onChange }: {
    label: string; desc: string; value: string | number; options: { value: string | number; label: string }[]; onChange: (v: string) => void;
  }) => (
    <div className="mb-4">
      <label className="text-xs font-bold text-stone-300 uppercase tracking-widest">{label}</label>
      <p className="text-[10px] text-stone-600 mt-0.5 mb-2 leading-relaxed">{desc}</p>
      <select value={value} onChange={e => onChange(e.target.value)}
        className="w-full bg-stone-800 border border-stone-700 text-stone-200 text-sm rounded-lg px-3 py-2 outline-none focus:border-stone-500 cursor-pointer">
        {options.map(o => <option key={String(o.value)} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );

  const InputRow = ({ label, desc, value, placeholder, onChange }: {
    label: string; desc: string; value: string; placeholder?: string; onChange: (v: string) => void;
  }) => (
    <div className="mb-4">
      <label className="text-xs font-bold text-stone-300 uppercase tracking-widest">{label}</label>
      <p className="text-[10px] text-stone-600 mt-0.5 mb-2 leading-relaxed">{desc}</p>
      <input type="text" value={value} placeholder={placeholder} onChange={e => onChange(e.target.value)}
        className="w-full bg-stone-800 border border-stone-700 text-stone-200 text-sm rounded-lg px-3 py-2 outline-none focus:border-stone-500 placeholder-stone-700" />
    </div>
  );

  const NumberInput = ({ label, desc, value, min, max, onChange }: {
    label: string; desc: string; value: number; min?: number; max?: number; onChange: (v: number) => void;
  }) => (
    <div className="mb-4">
      <label className="text-xs font-bold text-stone-300 uppercase tracking-widest">{label}</label>
      <p className="text-[10px] text-stone-600 mt-0.5 mb-2 leading-relaxed">{desc}</p>
      <input type="number" value={value} min={min} max={max} onChange={e => onChange(Number(e.target.value))}
        className="w-full bg-stone-800 border border-stone-700 text-stone-200 text-sm rounded-lg px-3 py-2 outline-none focus:border-stone-500" />
    </div>
  );

  const ColorChips = ({ label, desc, value, options, onChange }: {
    label: string; desc: string; value: string; options: { value: string; label: string; color: string }[]; onChange: (v: string) => void;
  }) => (
    <div className="mb-4">
      <label className="text-xs font-bold text-stone-300 uppercase tracking-widest">{label}</label>
      <p className="text-[10px] text-stone-600 mt-0.5 mb-2">{desc}</p>
      <div className="flex gap-2 flex-wrap">
        {options.map(o => (
          <button key={o.value} onClick={() => onChange(o.value)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider border transition-all ${value === o.value ? "border-stone-300 bg-stone-700 text-stone-100" : "border-stone-700 bg-stone-800/50 text-stone-500 hover:border-stone-500"}`}>
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: o.color }} />{o.label}
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center">
      <div className="absolute inset-0 bg-stone-950/85 backdrop-blur-lg" onClick={onClose} />
      <motion.div initial={{ opacity: 0, scale: 0.97, y: 12 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ duration: 0.2, ease: "easeOut" }}
        className="relative w-full max-w-3xl mx-4 bg-stone-900 border border-white/[0.08] rounded-2xl shadow-2xl overflow-hidden flex flex-col" style={{ maxHeight: "90vh" }}>

        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-stone-400/60 to-transparent" />

        {/* Header */}
        <div className="flex items-center justify-between px-7 py-4 border-b border-white/[0.06] shrink-0">
          <div className="flex items-center gap-3">
            <img src="/top_right_logo.png" alt="SDD" className="w-9 h-9 object-contain" />
            <div>
              <h2 className="text-base font-black text-stone-100 tracking-widest uppercase">System Settings</h2>
              <p className="text-[9px] text-stone-600 uppercase tracking-widest mt-0.5">Military Drill Analysis · SDD MCEME · 30+ parameters</p>
            </div>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full bg-stone-800 hover:bg-stone-700 flex items-center justify-center text-stone-400 hover:text-stone-200 transition-colors text-xl">×</button>
        </div>

        <div className="flex border-b border-white/[0.06] px-4 pt-2 overflow-x-auto shrink-0 gap-1">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`whitespace-nowrap px-3 py-2 text-[10px] font-black uppercase tracking-widest border-b-2 transition-all rounded-t ${activeTab === t.id ? "text-stone-100 border-stone-300 bg-stone-800/60" : "text-stone-600 border-transparent hover:text-stone-400 hover:bg-stone-800/30"}`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-7 py-5 min-h-0">

          {/* ─ CAMERA ─ */}
          {activeTab === "camera" && (
            <div>
              <Section title="Camera Assignment" />
              <p className="text-[10px] text-stone-600 mb-4">Assign which physical camera index maps to each evaluation angle.</p>
              {(["front", "side", "back"] as (keyof CameraMapping)[]).map(field => (
                <div key={field} className="flex items-center justify-between mb-3 p-4 bg-stone-800/40 rounded-xl border border-white/[0.05]">
                  <div>
                    <div className="text-xs font-black text-stone-200 uppercase tracking-widest">{field} Camera</div>
                    <div className="text-[10px] text-stone-600 mt-0.5">{field === "front" ? "Primary subject evaluation view" : field === "side" ? "Lateral posture & knee view" : "Rear alignment & arm view"}</div>
                  </div>
                  <div className="flex gap-2">
                    {[0, 1, 2].map(i => (
                      <button key={i} onClick={() => setLocalMap(p => ({ ...p, [field]: i }))}
                        className={`w-10 h-10 rounded-xl font-black text-sm transition-all ${localMap[field] === i ? "bg-stone-200 text-stone-950 shadow-lg" : "bg-stone-700/80 text-stone-400 hover:bg-stone-600 hover:text-stone-200"}`}>
                        {i}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
              <Section title="Camera Options" />
              <SelectRow label="Side Camera Position" desc="Whether the side camera is placed on the left or right side of the cadet." value={settings.side_camera_position} options={[{value: "left", label: "Left"}, {value: "right", label: "Right"}]} onChange={v => set("side_camera_position", v)} />
              <SliderRow label="FPS Cap" desc="Maximum frames per second to request from the camera hardware." min={5} max={60} step={5} value={settings.camera_fps_cap} unit=" fps" onChange={v => set("camera_fps_cap", v)} />
              <ToggleRow label="Flip Horizontal" desc="Mirror the camera feed left-to-right before processing." value={settings.camera_flip_horizontal} onChange={v => set("camera_flip_horizontal", v)} />
              <ToggleRow label="Flip Vertical" desc="Flip the camera feed upside-down before processing." value={settings.camera_flip_vertical} onChange={v => set("camera_flip_vertical", v)} />
            </div>
          )}

          {/* ─ AI ENGINE ─ */}
          {activeTab === "ai" && (
            <div>
              <Section title="Pose Detection Model" />
              <SliderRow label="Detection Confidence" desc="Minimum YOLO keypoint confidence. Lower catches more but raises false positives." min={0.1} max={0.95} step={0.05} value={settings.confidence} onChange={v => set("confidence", v)} />
              <SliderRow label="Keypoint Visibility" desc="Minimum per-keypoint visibility score to be used in evaluation calculations." min={0.1} max={0.9} step={0.05} value={settings.keypoint_visibility_threshold} onChange={v => set("keypoint_visibility_threshold", v)} />
              <SelectRow label="Inference Image Size" desc="Resolution used for YOLO inference. Larger = more accurate but slower." value={settings.image_size}
                options={[{ value: 320, label: "320px — Fastest" }, { value: 480, label: "480px — Fast" }, { value: 640, label: "640px — Balanced (Default)" }, { value: 960, label: "960px — Accurate" }, { value: 1280, label: "1280px — Maximum Accuracy" }]}
                onChange={v => set("image_size", Number(v))} />
              <NumberInput label="Max Detections Per Frame" desc="Upper bound on simultaneous persons tracked. Lower = faster processing." value={settings.max_detections} min={1} max={20} onChange={v => set("max_detections", v)} />
              <Section title="Tracking Algorithm" />
              <SelectRow label="Tracker" desc="Multi-object tracking algorithm for assigning stable IDs to detected cadets." value={settings.tracking_config}
                options={[{ value: "bytetrack.yaml", label: "ByteTrack — Fast, Efficient (Default)" }, { value: "botsort.yaml", label: "BotSORT — More Stable IDs" }]}
                onChange={v => set("tracking_config", v)} />
              <SliderRow label="Stale Detection Timeout" desc="Seconds before a non-updated detection is dropped from the fusion pool." min={0.5} max={10} step={0.5} value={settings.stale_detection_timeout} unit="s" onChange={v => set("stale_detection_timeout", v)} />
              <Section title="Performance" />
              <SliderRow label="Evaluation Loop FPS" desc="How many times per second the fusion evaluator scores the pose. Higher = more real-time." min={5} max={60} step={5} value={settings.evaluation_fps} unit=" fps" onChange={v => set("evaluation_fps", v)} />
              <ToggleRow label="Half Precision Inference (FP16)" desc="Use FP16 precision for GPU inference — faster but slightly less accurate." value={settings.prefer_half_precision} onChange={v => set("prefer_half_precision", v)} badge="GPU" />
            </div>
          )}

          {/* ─ EVALUATION / SCORING ─ */}
          {activeTab === "evaluation" && (
            <div>
              <Section title="Global Scoring" />
              <SliderRow label="Default Pass Threshold" desc="Minimum overall percentage score to receive a PASS verdict." min={50} max={100} step={1} value={settings.pass_threshold} unit="%" onChange={v => set("pass_threshold", v)} />
              <SliderRow label="Score Smoothing Window" desc="Number of recent evaluation frames to average. Higher = smoother but slower to react to changes." min={1} max={30} step={1} value={settings.score_smoothing_window} onChange={v => set("score_smoothing_window", v)} />
              <Section title="Per-Mode Thresholds" />
              <p className="text-[10px] text-stone-600 mb-4 leading-relaxed">Override the pass threshold for individual drill modes. Fine-tune difficulty per exercise.</p>
              <SliderRow label="Savadhan (Attention)" desc="SAVDHAN — full attention posture threshold." min={50} max={100} step={1} value={settings.savdhan_threshold} unit="%" onChange={v => set("savdhan_threshold", v)} />
              <SliderRow label="Vishram (At Ease)" desc="VISHRAM — relaxed at-ease posture threshold." min={50} max={100} step={1} value={settings.vishram_threshold} unit="%" onChange={v => set("vishram_threshold", v)} />
              <SliderRow label="Salute" desc="FRONT / BAYE / DAINE SALUTE posture threshold." min={50} max={100} step={1} value={settings.salute_threshold} unit="%" onChange={v => set("salute_threshold", v)} />
              <SliderRow label="Aaram Se" desc="AARAM SE — stand easy posture threshold." min={50} max={100} step={1} value={settings.aaram_se_threshold} unit="%" onChange={v => set("aaram_se_threshold", v)} />
            </div>
          )}

          {/* ─ VOICE ─ */}
          {activeTab === "voice" && (
            <div>
              <Section title="Voice Command Engine" />
              <ToggleRow label="Enable Voice Commands" desc="Allow drill modes to be switched using voice via the Whisper STT model." value={settings.voice_enabled} onChange={v => set("voice_enabled", v)} />
              <SelectRow label="Recognition Language" desc="Primary language hint passed to Whisper to improve command recognition." value={settings.voice_language}
                options={[{ value: "en", label: "English" }, { value: "hi", label: "Hindi (हिंदी)" }, { value: "auto", label: "Auto-detect (Slower)" }]}
                onChange={v => set("voice_language", v)} />
              <InputRow label="Initial Prompt" desc="Context hint provided to Whisper to improve drill command recognition. Helps reduce misrecognition." value={settings.voice_initial_prompt} placeholder="e.g. Military drill commands: savadhan, vishram..." onChange={v => set("voice_initial_prompt", v)} />
              <Section title="Recognized Commands" />
              <div className="grid grid-cols-2 gap-1.5">
                {["Savadhan / Attention", "Vishram / At Ease", "Samne Salute", "Baye Salute", "Daine Salute", "Aaram Se", "Dahine Murh", "Bayen Murh", "Pichhe Murh", "Khuli Line", "Nikat Line"].map(cmd => (
                  <div key={cmd} className="text-[10px] text-stone-500 font-mono px-3 py-2 bg-stone-800/40 rounded-lg border border-white/[0.04]">▸ {cmd}</div>
                ))}
              </div>
            </div>
          )}

          {/* ─ DISPLAY ─ */}
          {activeTab === "display" && (
            <div>
              <Section title="Camera Overlays" />
              <ToggleRow label="Show ID Overlay" desc="Render cadet track IDs above detected persons on the camera feed." value={settings.show_id_overlay} onChange={v => set("show_id_overlay", v)} />
              <ToggleRow label="Show Skeleton Overlay" desc="Draw pose skeleton keypoint lines on the live camera feed." value={settings.show_skeleton} onChange={v => set("show_skeleton", v)} />
              <ToggleRow label="Show Confidence Scores" desc="Display per-keypoint detection confidence percentages on the overlay." value={settings.show_confidence_score} onChange={v => set("show_confidence_score", v)} />
              <ColorChips label="Skeleton Color" desc="Color of the pose skeleton lines drawn on the camera feed."
                value={settings.skeleton_color}
                options={[{ value: "green", label: "Green", color: "#4ade80" }, { value: "white", label: "White", color: "#e7e5e4" }, { value: "red", label: "Red", color: "#f87171" }, { value: "yellow", label: "Yellow", color: "#facc15" }, { value: "cyan", label: "Cyan", color: "#22d3ee" }, { value: "orange", label: "Orange", color: "#fb923c" }]}
                onChange={v => set("skeleton_color", v)} />
              <SliderRow label="Overlay Opacity" desc="Transparency of all on-feed overlay elements (labels, skeleton, scores)." min={0.1} max={1.0} step={0.05} value={settings.overlay_opacity} onChange={v => set("overlay_opacity", v)} />
              <SelectRow label="Camera Label Position" desc="Where the camera name/index label appears on the video feed." value={settings.camera_label_position}
                options={[{ value: "top-left", label: "Top Left" }, { value: "top-right", label: "Top Right" }, { value: "bottom-left", label: "Bottom Left" }, { value: "bottom-right", label: "Bottom Right" }]}
                onChange={v => set("camera_label_position", v)} />
              <Section title="Alerts & Notifications" />
              <ToggleRow label="Visual Flash on State Change" desc="Flash the evaluation panel briefly when the PASS/FAIL verdict changes." value={settings.alert_visual_flash} onChange={v => set("alert_visual_flash", v)} />
              <ToggleRow label="Alert on PASS" desc="Show a browser notification when evaluation result changes to PASS." value={settings.alert_on_pass} onChange={v => set("alert_on_pass", v)} />
              <ToggleRow label="Alert on FAIL" desc="Show a browser notification when evaluation result changes to FAIL." value={settings.alert_on_fail} onChange={v => set("alert_on_fail", v)} />
            </div>
          )}

          {/* ─ SESSION ─ */}
          {activeTab === "session" && (
            <div>
              <Section title="Session Identity" />
              <InputRow label="Unit Name" desc="Name of the unit or batch being evaluated. Appears in exported reports." value={settings.unit_name} placeholder="e.g. 11 EME BN — A Company" onChange={v => set("unit_name", v)} />
              <InputRow label="Instructor Name" desc="Supervising instructor name. Appears in exported reports." value={settings.instructor_name} placeholder="e.g. Lt Col K Srinath" onChange={v => set("instructor_name", v)} />
              <Section title="Session Behaviour" />
              <ToggleRow label="Auto-Save Session" desc="Automatically save results to disk when the session ends." value={settings.auto_save_session} onChange={v => set("auto_save_session", v)} />
              <SelectRow label="Export Format" desc="File format for saved session result reports." value={settings.export_format}
                options={[{ value: "json", label: "JSON — Machine Readable" }, { value: "csv", label: "CSV — Spreadsheet" }, { value: "txt", label: "Plain Text — Human Report" }]}
                onChange={v => set("export_format", v)} />
              <NumberInput label="Session Duration Limit (minutes)" desc="Auto-end the session after this many minutes. Set 0 for unlimited." value={settings.session_duration_limit} min={0} max={480} onChange={v => set("session_duration_limit", v)} />
              <Section title="About" />
              <div className="p-4 bg-stone-800/40 rounded-xl border border-white/[0.05]">
                <div className="text-stone-200 text-sm font-semibold">Military Drill Analysis System</div>
                <div className="text-stone-500 text-xs mt-1">Simulation Development Division (SDD), MCEME</div>
                <div className="mt-3 pt-3 border-t border-white/[0.05] space-y-1">
                  <div className="text-stone-500 text-xs">Developed by <span className="text-stone-300 font-semibold">Janardhan & Shankumar</span></div>
                  <div className="text-stone-500 text-xs">Under guidance of <span className="text-stone-300 font-semibold">Lt Col K Srinath</span></div>
                </div>
              </div>
            </div>
          )}

          {/* ─ NETWORK ─ */}
          {activeTab === "network" && (
            <div>
              <Section title="Backend Connection" />
              <InputRow label="Backend Host" desc="Hostname or IP address of the FastAPI backend server." value={settings.backend_host} placeholder="localhost" onChange={v => set("backend_host", v)} />
              <NumberInput label="Backend Port" desc="Port the FastAPI backend is listening on." value={settings.backend_port} min={1} max={65535} onChange={v => set("backend_port", v)} />
              <SliderRow label="WebSocket Reconnect Interval" desc="Seconds to wait before re-attempting a dropped WebSocket connection." min={1} max={30} step={1} value={settings.ws_reconnect_interval} unit="s" onChange={v => set("ws_reconnect_interval", v)} />
              <Section title="API Reference" />
              <div className="space-y-1.5">
                {[
                  ["WS",   "/ws/telemetry",          "Live evaluation data stream"],
                  ["GET",  "/api/video_feed/{n}",    "MJPEG camera stream"],
                  ["POST", "/api/lock_cadet",         "Lock cadet by track ID"],
                  ["POST", "/api/voice_command",      "Submit audio for Whisper STT"],
                  ["GET",  "/api/settings",           "Fetch current settings"],
                  ["POST", "/api/settings",           "Update settings live"],
                  ["GET",  "/api/settings/reset",     "Reset settings to defaults"],
                ].map(([method, path, desc]) => (
                  <div key={path} className="flex items-center gap-2 text-[10px] font-mono px-3 py-2 bg-stone-900/60 rounded-lg border border-white/[0.04]">
                    <span className={`font-black min-w-[36px] ${method === "WS" ? "text-amber-500" : method === "GET" ? "text-emerald-500" : "text-blue-400"}`}>{method}</span>
                    <span className="text-stone-400 flex-1">{path}</span>
                    <span className="text-stone-700 text-[9px] hidden xl:block">{desc}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-7 py-3.5 border-t border-white/[0.06] bg-stone-950/50 shrink-0">
          <div className="flex items-center gap-3">
            <button onClick={handleReset} className="px-4 py-1.5 text-[10px] bg-stone-800 hover:bg-red-950/60 hover:text-red-400 border border-white/[0.06] hover:border-red-500/30 text-stone-500 rounded-lg font-black uppercase tracking-wider transition-all">
              ↺ Reset Defaults
            </button>
            <span className="text-[9px] text-stone-700 hidden sm:block">Changes are applied live to the backend</span>
          </div>
          <div className="flex gap-2">
            <button onClick={onClose} className="px-5 py-2 text-xs bg-stone-800 hover:bg-stone-700 text-stone-400 rounded-lg font-black uppercase tracking-wider transition-colors">Cancel</button>
            <button onClick={handleSave} disabled={saveStatus === "saving"}
              className={`px-6 py-2 text-xs rounded-lg font-black uppercase tracking-wider transition-all ${saveStatus === "saved" ? "bg-emerald-500 text-white" : saveStatus === "error" ? "bg-red-600 text-white" : "bg-stone-200 text-stone-950 hover:bg-white active:scale-95"}`}>
              {saveStatus === "saving" ? "Saving…" : saveStatus === "saved" ? "✓ Saved" : saveStatus === "error" ? "Error!" : "Save Settings"}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// ─── Launch Screen ────────────────────────────────────────────
function LaunchScreen({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  useEffect(() => {
    const seq = ["Initializing core neural matrix...", "Loading pose estimation models...", "Calibrating multi-camera telemetry...", "Establishing secure WebSocket streams...", "System Ready."];
    let step = 0;
    const iv = setInterval(() => {
      setProgress(p => { const n = p + 100 / seq.length; if (n >= 100) clearInterval(iv); return n; });
      setLogs(l => [...l, seq[step]]); step++;
      if (step >= seq.length) setTimeout(onComplete, 1200);
    }, 600);
    return () => clearInterval(iv);
  }, [onComplete]);
  return (
    <>
      <div className="fixed top-8 left-8 z-[100] pointer-events-none"><img src="/top_right_logo.png" alt="SDD" className="w-6 sm:w-8 md:w-12 lg:w-16 xl:w-20 2xl:w-24 h-auto object-contain drop-shadow-md" /></div>
      <motion.div className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, scale: 1.05 }} transition={{ duration: 0.8 }}>
        <div className="absolute inset-0 z-0 pointer-events-none">
          <img src="/hello.jpg" alt="bg" className="w-full h-full object-cover blur-md scale-105" />
          <div className="absolute inset-0 bg-black/20" />
          <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
            <h1 className="text-[10rem] lg:text-[18rem] font-black tracking-tighter text-white/5 select-none whitespace-nowrap">INDIAN ARMY</h1>
          </div>
        </div>
        <div className="relative z-10 flex flex-col items-center justify-center w-full max-w-lg mt-10">
          <div className="relative w-56 h-56 mb-12 flex items-center justify-center">
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 12, repeat: Infinity, ease: "linear" }} className="absolute inset-0 border border-stone-400/10 rounded-full" />
            <motion.div animate={{ rotate: -360 }} transition={{ duration: 18, repeat: Infinity, ease: "linear" }} className="absolute inset-4 border border-stone-400/30 rounded-full border-t-transparent border-b-transparent" />
            <div className="w-40 h-40 bg-stone-800/40 backdrop-blur-2xl rounded-full shadow-2xl flex items-center justify-center border border-white/5 p-2">
              <img src="/logo.jpeg" alt="Logo" className="w-full h-full object-cover rounded-full opacity-80 mix-blend-luminosity" />
            </div>
          </div>
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3, duration: 0.8 }} className="text-center mb-10">
            <h1 className="text-4xl font-black tracking-[0.2em] text-stone-100 uppercase mb-2 drop-shadow-md">Drill Command</h1>
            <p className="text-xs font-bold tracking-[0.3em] text-stone-400 uppercase">Analysis System</p>
          </motion.div>
          <div className="w-64 space-y-4">
            <div className="h-[2px] w-full bg-stone-800 rounded-full overflow-hidden relative">
              <motion.div className="absolute top-0 left-0 h-full bg-stone-300" initial={{ width: 0 }} animate={{ width: `${progress}%` }} transition={{ ease: "linear", duration: 0.1 }} />
            </div>
            <div className="h-6 flex items-center justify-center overflow-hidden">
              <AnimatePresence mode="wait">
                {logs.length > 0 && (
                  <motion.div key={logs.length} initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: -10, opacity: 0 }} className="text-[10px] font-bold tracking-widest text-slate-400 uppercase text-center">
                    {logs[logs.length - 1]}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </motion.div>
    </>
  );
}

// ─── Onboarding Screen ────────────────────────────────────────
function OnboardingScreen({ onNext }: { onNext: () => void }) {
  return (
    <>
      <div className="fixed top-8 left-8 z-[100] pointer-events-none"><img src="/top_right_logo.png" alt="SDD" className="w-6 sm:w-8 md:w-12 lg:w-16 xl:w-20 2xl:w-24 h-auto object-contain drop-shadow-md" /></div>
      <motion.div className="fixed inset-0 z-40 flex items-center justify-center overflow-hidden"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, x: -50, filter: "blur(10px)" }} transition={{ duration: 0.8, ease: "easeOut" }}>
        <div className="absolute inset-0 z-0 pointer-events-none">
          <img src="/hello2.jpg" alt="bg" className="w-full h-full object-cover blur-md scale-105" />
          <div className="absolute inset-0 bg-black/20" />
          <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
            <h1 className="text-[10rem] lg:text-[18rem] font-black tracking-tighter text-white/5 select-none whitespace-nowrap opacity-50">INDIAN ARMY</h1>
          </div>
        </div>
        <div className="absolute inset-0 pointer-events-none z-0">
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: "40px 40px" }} />
        </div>
        <div className="bg-stone-900/40 backdrop-blur-3xl shadow-2xl border border-white/5 p-12 lg:p-16 rounded-[2.5rem] max-w-7xl w-full mx-6 relative z-10 overflow-hidden">
          <img src="/hello.jpg" alt="hero" className="absolute top-0 right-0 w-[300px] lg:w-[450px] h-auto object-contain opacity-40 rounded-bl-[100px] mix-blend-luminosity" />
          <motion.div className="relative z-10" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 1, ease: "easeOut" }}>
            <div className="flex items-center space-x-4 mb-6">
              <img src="/logo.jpeg" alt="Logo" className="w-10 h-10 object-cover rounded-full shadow-lg border border-white/10 mix-blend-luminosity" />
              <h3 className="text-xs font-bold text-stone-400 tracking-[0.4em] uppercase opacity-90">Simulation Development Division (SDD), MCEME</h3>
            </div>
            <h1 className="text-5xl lg:text-[5.5rem] font-black text-stone-100 tracking-tighter mb-8 leading-[1.05] drop-shadow-md">
              Military Drill <br /><span className="text-transparent bg-clip-text bg-gradient-to-r from-stone-400 via-stone-300 to-stone-500">Analysis System.</span>
            </h1>
            <div className="flex items-center space-x-4 mb-10">
              <div className="w-32 h-[2px] bg-gradient-to-r from-stone-500 to-stone-400 rounded-full" />
              <div className="w-4 h-[2px] bg-stone-400 rounded-full" />
              <div className="w-2 h-[2px] bg-stone-400 rounded-full opacity-50" />
            </div>
            <p className="text-lg lg:text-xl text-stone-400 max-w-3xl leading-relaxed mb-14 font-medium">
              A professional evaluation suite for rigorous posture and alignment tracking. Initialize the workspace to begin real-time, multi-camera drill compliance assessment powered by state-of-the-art neural engines.
            </p>
            <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mt-4">
              <div className="flex flex-col space-y-2 text-stone-400">
                <p className="text-sm tracking-wide font-medium"><span className="text-stone-300 font-bold uppercase tracking-widest text-xs mr-2">Project By:</span>Janardhan &amp; Shankumar</p>
                <p className="text-xs tracking-wider uppercase font-bold opacity-70">Under the Guidance &amp; Mentorship of <span className="text-stone-300">Lt Col K Srinath</span></p>
              </div>
              <button onClick={onNext} className="group shrink-0 flex items-center justify-center space-x-4 bg-stone-800 text-stone-100 border border-white/10 px-12 py-4 rounded-full font-bold text-lg hover:bg-stone-700 active:scale-95 transition-all shadow-xl">
                <span className="tracking-widest uppercase">Start</span>
                <ChevronRightCircle className="w-6 h-6 group-hover:translate-x-1 transition-transform opacity-50 group-hover:opacity-100" />
              </button>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </>
  );
}

// ─── Telemetry Card ───────────────────────────────────────────
function TelemetryGaugeCard({ label, value, index }: { label: string; value: any; index: number }) {
  if (typeof value === "number") return null;
  const isPass = value.status === "pass";
  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.04 }}
      className={`p-3.5 rounded-xl border transition-all group ${isPass ? "border-emerald-500/20 bg-emerald-950/20 hover:border-emerald-500/40" : "border-red-500/20 bg-red-950/10 hover:border-red-500/40"}`}>
      <div className="flex items-start justify-between mb-2">
        <h4 className="text-[10px] font-black text-stone-300 tracking-wider uppercase leading-tight flex-1 mr-2">{label}</h4>
        <div className={`shrink-0 flex items-center gap-1 text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest ${isPass ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}`}>
          <span className={`w-1 h-1 rounded-full ${isPass ? "bg-emerald-400" : "bg-red-400"}`} />
          {isPass ? "PASS" : "FAIL"}
        </div>
      </div>
      <div className="text-[10px] text-stone-500 font-mono leading-relaxed">{value.reason}</div>
      <div className="mt-2 h-0.5 w-full bg-stone-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${isPass ? "bg-emerald-500/60 w-full" : "bg-red-500/60 w-2/3"}`} />
      </div>
    </motion.div>
  );
}

// ─── Score Ring ───────────────────────────────────────────────
function ScoreRing({ score, isPass, isInitializing }: { score: number; isPass: boolean; isInitializing: boolean }) {
  const r = 38, circ = 2 * Math.PI * r;
  const color = isInitializing ? "#57534e" : isPass ? "#34d399" : "#f87171";
  return (
    <div className="relative w-28 h-28 flex items-center justify-center">
      <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#292524" strokeWidth="6" />
        <motion.circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="6" strokeLinecap="round"
          strokeDasharray={circ} initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ - (score / 100) * circ }} transition={{ duration: 1, ease: "easeOut" }} />
      </svg>
      <div className="relative z-10 text-center">
        <div className="text-2xl font-black tabular-nums" style={{ color }}>{isInitializing ? "—" : `${score}%`}</div>
        <div className="text-[8px] font-bold text-stone-600 uppercase tracking-widest mt-0.5">Overall</div>
      </div>
    </div>
  );
}

// ─── Dashboard ────────────────────────────────────────────────
import { globalCadetTracker } from "@/utils/CadetTracker";

function Dashboard({ activeCadet, onComplete }: { activeCadet: any; onComplete: (results: any[]) => void }) {
  const BASE_URL = "http://localhost:8000";
  const [cameraMap, setCameraMap] = useState<CameraMapping>({ front: 0, side: 1, back: 2 });
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [selectedCam, setSelectedCam] = useState(0);
  const [selectedCadet, setSelectedCadet] = useState<string | null>(null);
  const [sessionResults, setSessionResults] = useState<{ drill: string; pass: boolean; score: number }[]>([]);
  const [wsStatus, setWsStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  const [telemetry, setTelemetry] = useState<{ metrics: Record<string, any>; overall_score: number; status: string; detected_ids: number[]; active_mode?: string; last_command?: string; calibration_step?: number; calibration_completed?: boolean; locked_track_id?: number | null; }>({
    metrics: {}, overall_score: 0, status: "Initializing...", detected_ids: [], active_mode: "SAVDHAN", last_command: "", calibration_step: 1, calibration_completed: false, locked_track_id: null
  });
  const [settings, setSettings] = useState<any>({ camera_label_position: "top-left" });
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const fetchSettings = () => fetch(`${BASE_URL}/api/settings`).then(r => r.json()).then(setSettings).catch(() => {});

  useEffect(() => {
    fetchSettings();
    try { const s = localStorage.getItem("cameraMapping"); if (s) { const p = JSON.parse(s); setCameraMap(p); setSelectedCam(p.front); } } catch {}
  }, []);

  const persistMapping = (map: CameraMapping) => { localStorage.setItem("cameraMapping", JSON.stringify(map)); setCameraMap(map); setSelectedCam(map.front); };

  const connectWS = useCallback(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/telemetry");
    wsRef.current = ws;
    ws.onopen = () => setWsStatus("connected");
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        const { overall_score, status, detected_ids, active_mode, last_command, calibration_step, calibration_completed, locked_track_id, ...metrics } = data;
        const clean: Record<string, any> = {};
        for (const k in metrics) {
          if (metrics[k] && metrics[k].status !== "not_evaluable") {
            clean[k.split("_").map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")] = metrics[k];
          }
        }
        setTelemetry({ metrics: clean, overall_score: overall_score || 0, status: status || "Initializing...", detected_ids: detected_ids || [], active_mode: active_mode || "SAVDHAN", last_command: last_command || "", calibration_step: calibration_step || 1, calibration_completed: !!calibration_completed, locked_track_id: locked_track_id });
      } catch {}
    };
    ws.onclose = () => { setWsStatus("disconnected"); reconnectTimeout.current = setTimeout(connectWS, 3000); };
    ws.onerror = () => ws.close();
  }, []);

  useEffect(() => { connectWS(); return () => { reconnectTimeout.current && clearTimeout(reconnectTimeout.current); wsRef.current?.close(); }; }, [connectWS]);

  useEffect(() => {
    if (telemetry.active_mode === "CALIBRATION" && telemetry.calibration_completed) {
      if (telemetry.locked_track_id !== undefined && telemetry.locked_track_id !== null) {
        setSelectedCadet(telemetry.locked_track_id.toString());
      }
      setTimeout(() => changeMode("SAVDHAN"), 3000);
    }
  }, [telemetry.active_mode, telemetry.calibration_completed, telemetry.locked_track_id]);

  const changeMode = (mode: string) => { wsRef.current?.readyState === WebSocket.OPEN && wsRef.current.send(JSON.stringify({ mode })); };
  const lockCadet = async (id: number) => { setSelectedCadet(id.toString()); try { await fetch(`${BASE_URL}/api/lock_cadet`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ track_id: id, source_camera: selectedCam }) }); } catch {} };
  const saveSession = async () => {
    const p = telemetry.overall_score >= 80;
    const drill = telemetry.active_mode || "SAVDHAN";
    const r = [...sessionResults, { drill, pass: p, score: telemetry.overall_score }];
    setSessionResults(r);
    
    if (activeCadet && activeCadet.id) {
      try {
        await fetch(`${BASE_URL}/api/sessions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            cadet_id: activeCadet.id,
            drill_type: drill,
            score: telemetry.overall_score,
            is_pass: p
          })
        });
      } catch (e) {
        console.error("Failed to save session", e);
      }
    }
    
    onComplete(r);
  };

  const isPass = ["Excellent", "Good", "PASS"].includes(telemetry.status);
  const isInit = telemetry.status === "Initializing...";
  const drillModes = [
    { label: "Savadhan", val: "SAVDHAN", s: "SVD" }, 
    { label: "Vishram", val: "VISHRAM", s: "VSH" }, 
    { label: "Salute", val: "FRONT_SALUTE", s: "SLT" }, 
    { label: "Aaram Se", val: "AARAM_SE", s: "ARM" },
    { label: "Dahine Murh", val: "DAHINE_MURH", s: "DHM" },
    { label: "Bayen Murh", val: "BAYEN_MURH", s: "BYM" },
    { label: "Pichhe Murh", val: "PICHHE_MURH", s: "PCM" },
    { label: "Khuli Line", val: "KHULI_LINE_CHAL", s: "KLC" },
    { label: "Nikat Line", val: "NIKAT_LINE_CHAL", s: "NLC" },
    { label: "Saj", val: "SAJ", s: "SAJ" },
    { label: "Visarjan", val: "VISARJAN", s: "VSJ" },
    { label: "Tej Chal", val: "TEJ_CHAL", s: "TJC" },
    { label: "Thaam (Halt)", val: "THAAM", s: "THM" },
    { label: "Marching Salute (Front)", val: "MARCHING_FRONT_SALUTE", s: "MSF" },
    { label: "Marching Salute (Right)", val: "MARCHING_DAINE_SALUTE", s: "MSR" },
    { label: "Marching Salute (Left)", val: "MARCHING_BAYE_SALUTE", s: "MSL" },
    { label: "Marching Turn (Dahine)", val: "MARCHING_TURN_DAHINE", s: "MTD" },
    { label: "Marching Turn (Bayen)", val: "MARCHING_TURN_BAYEN", s: "MTB" },
    { label: "Marching Turn (Pichhe)", val: "MARCHING_TURN_PICHHE", s: "MTP" }
  ];
  const camPos = ["front", "side", "back"] as (keyof CameraMapping)[];

  return (
    <motion.div className="h-screen w-full flex flex-col font-sans bg-stone-950 text-stone-100 overflow-hidden relative" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6 }}>
      <SettingsModal isOpen={isSettingsOpen} onClose={() => { setIsSettingsOpen(false); fetchSettings(); }} mapping={cameraMap} onSave={persistMapping} baseUrl={BASE_URL} />
      <div className="absolute inset-0 z-0 pointer-events-none">
        <img src="/hello2.jpg" alt="bg" className="w-full h-full object-cover blur-2xl scale-110 opacity-10" />
        <div className="absolute inset-0 bg-stone-950/95" />
        <div className="absolute inset-0 opacity-[0.025]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: "32px 32px" }} />
      </div>

      {/* Header */}
      <header className="h-14 flex items-center justify-between px-5 lg:px-6 border-b border-white/[0.06] bg-stone-900/70 backdrop-blur-xl relative z-40 shrink-0">
        <div className="flex items-center gap-3">
          <img src="/top_right_logo.png" alt="SDD" className="w-8 h-8 object-contain" />
          <div>
            <div className="text-[11px] font-black tracking-[0.15em] uppercase text-stone-100 leading-none">Military Drill <span className="text-stone-500 font-normal">Analysis System</span></div>
            <div className="text-[8px] font-bold tracking-[0.3em] text-stone-700 uppercase mt-0.5">SDD · MCEME · REAL-TIME</div>
          </div>
        </div>
        <div className="hidden lg:flex flex-1 mx-4 overflow-x-auto no-scrollbar items-center gap-1 bg-stone-900/80 border border-white/[0.04] rounded-full p-1 shadow-inner">
          {drillModes.map(m => (
            <button key={m.val} onClick={() => changeMode(m.val)}
              className={`shrink-0 px-4 py-1.5 text-[10px] font-black tracking-[0.1em] uppercase rounded-full transition-all duration-300 ${telemetry.active_mode === m.val ? "bg-emerald-500 text-stone-950 shadow-[0_0_15px_rgba(16,185,129,0.3)]" : "text-stone-500 hover:bg-stone-800/80 hover:text-stone-200"}`}>
              {m.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <SessionTimer running={wsStatus === "connected"} />
          <div className="w-px h-6 bg-white/5" />
          <LiveClock />
          <div className="w-px h-6 bg-white/5" />
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[9px] font-black uppercase tracking-widest ${wsStatus === "connected" ? "border-emerald-500/30 bg-emerald-950/30 text-emerald-400" : "border-red-500/30 bg-red-950/30 text-red-400"}`}>
            {wsStatus === "connected" ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}{wsStatus}
          </div>
          <button onClick={() => setIsSettingsOpen(true)} className="p-2 bg-stone-800/80 hover:bg-stone-700 border border-white/[0.06] rounded-lg text-stone-500 hover:text-stone-200 transition-colors">
            <Settings className="w-3.5 h-3.5" />
          </button>
          <button onClick={saveSession} className="flex items-center gap-2 px-4 py-2 bg-stone-800 hover:bg-stone-700 border border-white/[0.06] text-stone-400 hover:text-stone-200 rounded-lg text-[10px] font-black uppercase tracking-wider transition-colors">
            <LogOut className="w-3 h-3" />End Session
          </button>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 p-3 lg:p-4 overflow-hidden flex gap-3 relative z-10 min-h-0">
        {/* Sidebar */}
        <div className="w-48 xl:w-52 flex flex-col gap-3 shrink-0">
          {camPos.map((pos, idx) => {
            const camId = cameraMap[pos]; const isSel = selectedCam === camId;
            return (
              <motion.div key={pos} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.1 }}
                onClick={() => setSelectedCam(camId)}
                className={`flex-1 relative rounded-xl overflow-hidden cursor-pointer border transition-all duration-200 group ${isSel ? "border-stone-400/60 shadow-[0_0_24px_rgba(120,113,108,0.15)]" : "border-white/[0.06] hover:border-stone-600/60"}`}>
                <div className={`absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-2.5 py-1.5 ${isSel ? "bg-stone-950/80" : "bg-stone-950/60"} backdrop-blur-sm border-b border-white/[0.06]`}>
                  <span className="text-[8px] font-black tracking-[0.2em] text-stone-300 uppercase">{pos}</span>
                  <div className="flex items-center gap-1">
                    <span className={`w-1.5 h-1.5 rounded-full ${isSel ? "bg-red-500 animate-pulse" : "bg-stone-700"}`} />
                    <span className="text-[7px] font-mono text-stone-600">C{camId}</span>
                  </div>
                </div>
                <img src={`http://localhost:8000/api/video_feed/${camId}`} alt={pos}
                  className={`w-full h-full object-cover mt-7 transition-all relative z-10 ${isSel ? "opacity-100" : "opacity-40 group-hover:opacity-70"}`}
                  onLoad={e => {
                    const sibling = e.currentTarget.nextElementSibling as HTMLElement;
                    if (sibling) sibling.style.display = "none";
                  }}
                  onError={e => { 
                    e.currentTarget.style.display = "none";
                    const sibling = e.currentTarget.nextElementSibling as HTMLElement;
                    if (sibling) sibling.style.display = "flex";
                  }} />
                <div className="absolute inset-0 mt-7 flex flex-col items-center justify-center pointer-events-none z-0 bg-stone-900/60">
                  <motion.div animate={{ opacity: [0.4, 0.9, 0.4] }} transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }} className="flex flex-col items-center">
                    <WifiOff className="w-4 h-4 text-red-500/60 mb-1.5" />
                    <span className="text-[7px] font-black tracking-[0.2em] uppercase text-red-500/80">No Signal</span>
                  </motion.div>
                </div>

                {isSel && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-emerald-400/80 to-transparent z-30" />}
                {!isSel && <div className="absolute inset-0 mt-7 pointer-events-none z-20 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.5)_50%)] bg-[length:100%_4px] opacity-20 mix-blend-overlay"></div>}
              </motion.div>
            );
          })}
        </div>

        {/* Main Camera View */}
        <div className="flex-1 relative rounded-2xl overflow-hidden bg-stone-900/50 backdrop-blur-sm border border-white/[0.06] flex flex-col min-w-0">
          <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-stone-400/40 to-transparent z-20" />
          <div className={`absolute z-20 flex items-center gap-2 
            ${settings.camera_label_position === "top-right" ? "top-3 right-3 flex-row-reverse" : 
              settings.camera_label_position === "bottom-left" ? "bottom-3 left-3" : 
              settings.camera_label_position === "bottom-right" ? "bottom-3 right-3 flex-row-reverse" : 
              "top-3 left-3"}`}>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-stone-950/80 backdrop-blur border border-white/[0.08] rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
              <span className="text-[9px] font-black tracking-widest text-stone-200 uppercase">CAM {selectedCam} · {selectedCam === cameraMap.front ? "FRONT" : selectedCam === cameraMap.side ? "SIDE" : "BACK"}</span>
            </div>
            {telemetry.active_mode && <div className="px-3 py-1.5 bg-stone-950/80 backdrop-blur border border-stone-600/30 rounded-full text-[9px] font-black text-stone-300 uppercase tracking-widest">◆ {telemetry.active_mode}</div>}
          </div>
          <div className="lg:hidden absolute top-3 right-3 z-20 flex gap-1.5">
            {drillModes.map(m => (
              <button key={m.val} onClick={() => changeMode(m.val)} className={`px-2 py-1 text-[8px] font-black uppercase tracking-widest rounded-full transition-all ${telemetry.active_mode === m.val ? "bg-stone-200 text-stone-950" : "bg-stone-900/80 border border-white/[0.06] text-stone-500"}`}>{m.s}</button>
            ))}
          </div>
          <div className="w-full h-full relative flex items-center justify-center bg-stone-950/20">
            <img src={`http://localhost:8000/api/video_feed/${selectedCam}`} alt="Feed" className="w-full h-full object-cover relative z-10" 
              onLoad={e => {
                const sibling = e.currentTarget.nextElementSibling as HTMLElement;
                if (sibling && sibling.id === "main-no-signal") sibling.style.display = "none";
              }}
              onError={e => { 
                e.currentTarget.style.display = "none";
                const sibling = e.currentTarget.nextElementSibling as HTMLElement;
                if (sibling && sibling.id === "main-no-signal") sibling.style.display = "flex";
              }} />
            <div id="main-no-signal" className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-0">
              <motion.div animate={{ opacity: [0.3, 0.7, 0.3], scale: [0.98, 1, 0.98] }} transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }} className="flex flex-col items-center">
                <WifiOff className="w-10 h-10 text-red-500/50 mb-3" />
                <span className="text-[14px] font-black tracking-[0.3em] uppercase text-red-500/80">Camera Offline</span>
                <span className="text-[10px] font-mono tracking-widest text-stone-600 mt-2 uppercase">Awaiting Feed Stream...</span>
              </motion.div>
            </div>

            {!selectedCadet && selectedCam === cameraMap.front && (
              <div className="absolute inset-0 z-30 flex flex-col items-center justify-center pointer-events-none bg-stone-950/20 backdrop-blur-[2px]">
                <div className="relative mb-8">
                  <motion.div animate={{ scale: [1, 1.4, 1], opacity: [0.4, 0, 0.4] }} transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }} className="absolute inset-0 -m-6 rounded-full border border-emerald-500/40" />
                  <motion.div animate={{ rotate: 90 }} transition={{ duration: 10, repeat: Infinity, ease: "linear" }} className="w-20 h-20 rounded-full border border-emerald-500/50 flex items-center justify-center border-t-transparent shadow-[0_0_20px_rgba(16,185,129,0.2)]">
                    <Crosshair className="w-8 h-8 text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                  </motion.div>
                </div>
                <p className="text-[12px] font-black text-emerald-400/80 uppercase tracking-[0.4em] mb-6 drop-shadow-md">Awaiting Target Acquisition</p>
                <div className="flex flex-wrap gap-4 pointer-events-auto justify-center max-w-lg">
                  {telemetry.detected_ids?.length > 0
                    ? telemetry.detected_ids.map(id => (
                        <button key={id} onClick={() => lockCadet(id)} className="group flex items-center gap-2 px-6 py-2.5 bg-stone-900/90 border border-emerald-500/30 text-emerald-100 rounded-full font-black text-[11px] uppercase tracking-widest hover:bg-stone-800 hover:border-emerald-400 hover:shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all">
                          <Target className="w-4 h-4 text-emerald-500 group-hover:animate-spin-slow" />Lock ID {id}
                        </button>
                      ))
                    : <div className="text-emerald-500/70 font-mono text-[11px] uppercase tracking-widest animate-pulse">Scanning environment...</div>}
                </div>
              </div>
            )}
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-stone-950/80 to-transparent z-10 flex items-end px-4 pb-2">
            <div className="flex items-center gap-4 text-[8px] font-mono text-stone-700 uppercase tracking-widest">
              <span>MJPEG STREAM</span><span>·</span><span>YOLO11n-POSE</span><span>·</span><span>BYTETRACK</span>
              {selectedCadet && <><span>·</span><span className="text-stone-400">LOCKED: ID-{selectedCadet}</span></>}
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="w-72 xl:w-80 shrink-0 flex flex-col gap-3 h-full min-h-0">
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            className="bg-stone-900/60 backdrop-blur-sm border border-white/[0.06] rounded-2xl p-4 shrink-0 relative overflow-hidden">
            <div className={`absolute top-0 left-0 right-0 h-0.5 transition-colors ${isInit ? "bg-stone-700" : isPass ? "bg-emerald-400" : "bg-red-500"}`} />
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-[9px] font-black tracking-[0.25em] text-stone-600 uppercase">Live Evaluation</h3>
              <div className={`text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest ${wsStatus === "connected" ? "bg-emerald-950/50 text-emerald-500" : "bg-stone-800 text-stone-600"}`}>
                {wsStatus === "connected" ? "● LIVE" : "○ OFFLINE"}
              </div>
            </div>
            <div className="flex items-center gap-4 mb-3">
              <ScoreRing score={telemetry.overall_score} isPass={isPass} isInitializing={isInit} />
              <div className="flex-1">
                <div className="text-[9px] font-black text-stone-500 uppercase tracking-widest mb-1">Verdict</div>
                <div className={`text-2xl font-black uppercase tracking-wider drop-shadow-md ${isInit ? "text-stone-600" : isPass ? "text-emerald-400" : "text-red-400"}`}>{isInit ? "WAITING" : isPass ? "PASS" : "FAIL"}</div>
                <div className="text-[9px] font-black text-stone-500 uppercase tracking-widest mt-3 mb-0.5">Target</div>
                <div className="text-xs font-black text-stone-300 uppercase tracking-wider">{selectedCadet ? `Cadet ${selectedCadet}` : "Unassigned"}</div>
                <div className="text-[9px] font-black text-stone-500 uppercase tracking-widest mt-3 mb-0.5">Mode</div>
                <div className="text-xs font-black text-stone-300 uppercase tracking-wider">{telemetry.active_mode?.replace(/_/g, " ") || "UNKNOWN"}</div>
              </div>
            </div>
            {!isInit && (
              <div>
                <div className="h-1 bg-stone-800 rounded-full overflow-hidden">
                  <motion.div className={`h-full rounded-full ${isPass ? "bg-emerald-400" : "bg-red-500"}`} initial={{ width: 0 }} animate={{ width: `${telemetry.overall_score}%` }} transition={{ duration: 0.8 }} />
                </div>
                <div className="flex justify-between text-[8px] font-mono text-stone-700 mt-1"><span>0</span><span>THRESHOLD</span><span>100</span></div>
              </div>
            )}
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
            className="flex-1 min-h-0 bg-stone-900/60 backdrop-blur-sm border border-white/[0.06] rounded-2xl p-4 flex flex-col">
            <div className="flex items-center justify-between mb-3 shrink-0">
              <h3 className="text-[9px] font-black tracking-[0.25em] text-stone-600 uppercase flex items-center gap-2"><BarChart3 className="w-3 h-3" />Diagnostic Breakdown</h3>
              {Object.keys(telemetry.metrics).length > 0 && <span className="text-[8px] font-mono text-stone-700">{Object.keys(telemetry.metrics).length} metrics</span>}
            </div>
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {Object.keys(telemetry.metrics).length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full py-8 gap-3">
                  <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ duration: 2, repeat: Infinity }}><Activity className="w-8 h-8 text-stone-800" /></motion.div>
                  <span className="text-[9px] text-stone-700 uppercase tracking-widest font-bold">Awaiting data stream...</span>
                </div>
              ) : (
                Object.entries(telemetry.metrics).map(([label, value], i) => <TelemetryGaugeCard key={label} label={label} value={value} index={i} />)
              )}
            </div>
          </motion.div>
        </div>
      </main>

      <AnimatePresence>
        {telemetry.active_mode === "CALIBRATION" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-stone-950/85 backdrop-blur-md">
            {telemetry.calibration_completed ? (
              <motion.div initial={{ scale: 0.8 }} animate={{ scale: 1 }} className="flex flex-col items-center text-emerald-400">
                <CheckCircle2 className="w-24 h-24 mb-6" />
                <h2 className="text-4xl font-black uppercase tracking-[0.2em] mb-2">Calibration Complete</h2>
                <p className="text-emerald-500/80 tracking-widest font-mono text-sm">Cameras Mapped. ID Locked. Initiating Drill Evaluation...</p>
              </motion.div>
            ) : (
              <div className="flex flex-col items-center">
                <Activity className="w-16 h-16 text-emerald-500 mb-6 animate-pulse" />
                <h2 className="text-stone-400 text-sm font-black uppercase tracking-[0.3em] mb-4">Auto-Calibration Sequence</h2>
                <h1 className="text-5xl font-black text-white uppercase tracking-wider mb-8 text-center max-w-2xl leading-tight">
                  {telemetry.calibration_step === 1 && "Raise your RIGHT hand"}
                  {telemetry.calibration_step === 2 && "Raise your LEFT hand"}
                  {telemetry.calibration_step === 3 && "Turn to your RIGHT side"}
                </h1>
                <div className="flex gap-4">
                  {[1, 2, 3].map(step => (
                    <div key={step} className={`w-16 h-2 rounded-full ${telemetry.calibration_step! > step ? "bg-emerald-500" : telemetry.calibration_step === step ? "bg-emerald-400 animate-pulse" : "bg-stone-800"}`} />
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status Bar */}
      <div className="h-7 shrink-0 border-t border-white/[0.04] bg-stone-900/60 backdrop-blur flex items-center justify-between px-5 relative z-20">
        <div className="flex items-center gap-5 text-[8px] font-mono text-stone-700 uppercase tracking-widest">
          <span className={wsStatus === "connected" ? "text-emerald-700" : "text-red-900"}>● WS {wsStatus}</span>
          <span>· YOLO11n-POSE · BYTETRACK</span><span>· SDD MCEME</span>
        </div>
        <div className="flex items-center gap-4 text-[8px] font-mono text-stone-700 uppercase tracking-widest">
          <span>Janardhan &amp; Shankumar</span><span>·</span><span>Lt Col K Srinath</span>
        </div>
      </div>
    </motion.div>
  );
}

// ─── Results Screen ───────────────────────────────────────────
function ResultsScreen({ results, onRestart }: { results: any[]; onRestart: () => void }) {
  const passed = results.filter(r => r.pass).length, total = results.length;
  return (
    <motion.div className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="absolute inset-0">
        <img src="/hello2.jpg" alt="bg" className="w-full h-full object-cover blur-lg scale-110 opacity-20" />
        <div className="absolute inset-0 bg-stone-950/92" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: "40px 40px" }} />
      </div>
      <div className="fixed top-8 left-8 z-[100]"><img src="/top_right_logo.png" alt="SDD" className="w-6 sm:w-8 md:w-12 lg:w-16 xl:w-20 2xl:w-24 h-auto object-contain" /></div>
      <div className="relative z-10 w-full max-w-3xl mx-6 p-8 bg-stone-900/80 backdrop-blur-3xl border border-white/10 rounded-3xl shadow-2xl">
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-stone-400/50 to-transparent rounded-t-3xl" />
        <div className="text-center mb-8">
          <div className="text-[9px] font-black tracking-[0.3em] text-stone-600 uppercase mb-2">Session Complete</div>
          <h1 className="text-3xl font-black text-stone-100 uppercase tracking-wider">Final Evaluation</h1>
        </div>
        <div className="grid grid-cols-3 gap-4 mb-8 text-center">
          {[{ label: "Total", value: total, color: "text-stone-200" }, { label: "Passed", value: passed, color: "text-emerald-400" }, { label: "Failed", value: total - passed, color: "text-red-400" }].map(item => (
            <div key={item.label} className="p-5 bg-stone-800/50 rounded-2xl border border-white/[0.06]">
              <div className="text-[9px] font-black text-stone-600 tracking-widest uppercase mb-2">{item.label}</div>
              <div className={`text-4xl font-black ${item.color}`}>{item.value}</div>
            </div>
          ))}
        </div>
        <div className="space-y-2 mb-8 max-h-[40vh] overflow-y-auto pr-2">
          {results.map((r, i) => (
            <div key={i} className="flex items-center justify-between p-4 bg-stone-800/50 border border-white/[0.06] rounded-xl">
              <div className="flex items-center space-x-4">
                <span className="text-stone-700 font-mono font-bold text-sm">{(i + 1).toString().padStart(2, "0")}</span>
                <span className="text-stone-200 font-bold">{r.drill}</span>
              </div>
              <div className="flex items-center gap-5">
                <div className="text-right"><div className="text-[9px] text-stone-600 uppercase tracking-widest">Score</div><div className="font-mono text-stone-200 font-bold">{r.score}%</div></div>
                <div className={`px-4 py-1.5 rounded-lg font-black text-[10px] uppercase tracking-wider border ${r.pass ? "bg-emerald-950/50 text-emerald-400 border-emerald-500/30" : "bg-red-950/50 text-red-400 border-red-500/30"}`}>{r.pass ? "PASS" : "FAIL"}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="text-center">
          <button onClick={onRestart} className="px-10 py-4 bg-stone-200 text-stone-950 font-black uppercase tracking-widest rounded-full hover:bg-white active:scale-95 transition-all shadow-xl">New Session</button>
        </div>
      </div>
    </motion.div>
  );
}

// ─── App Entry ────────────────────────────────────────────────
export default function App() {
  const [appState, setAppState] = useState<"launch" | "onboarding" | "registration" | "dashboard" | "results">("launch");
  const [activeCadet, setActiveCadet] = useState<any>(null);
  const [finalResults, setFinalResults] = useState<any[]>([]);
  return (
    <AnimatePresence mode="wait">
      {appState === "launch" && <LaunchScreen key="launch" onComplete={() => setAppState("onboarding")} />}
      {appState === "onboarding" && <OnboardingScreen key="onboard" onNext={() => setAppState("registration")} />}
      {appState === "registration" && (
        <RegistrationScreen 
          key="registration" 
          onComplete={(cadet) => {
            setActiveCadet(cadet);
            setAppState("dashboard");
          }} 
        />
      )}
      {appState === "dashboard" && <Dashboard key="dashboard" activeCadet={activeCadet} onComplete={r => { setFinalResults(r); setAppState("results"); }} />}
      {appState === "results" && <ResultsScreen key="results" results={finalResults} onRestart={() => setAppState("launch")} />}
    </AnimatePresence>
  );
}
