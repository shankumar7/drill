"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import { Gauge } from "../components/Gauge";
import { Activity, Shield, Users, Settings, LogOut, ChevronRightCircle, Mic, CheckCircle, XCircle, Crosshair, Wifi, WifiOff, Target, Clock, BarChart3, Sliders } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

type CameraMapping = { front: number; side: number; back: number; };
type AppSettings = {
  confidence: number; pass_threshold: number; voice_language: string;
  show_skeleton: boolean; show_id_overlay: boolean; auto_save_session: boolean; image_size: number;
};

// ─── Live Clock ─────────────────────────────────────────────
function LiveClock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => { const t = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(t); }, []);
  return (
    <div className="flex flex-col items-end">
      <span className="text-xs font-mono font-bold text-stone-200 tracking-widest tabular-nums">
        {time.toLocaleTimeString('en-IN', { hour12: false })}
      </span>
      <span className="text-[9px] font-mono text-stone-600 tracking-widest">
        {time.toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })}
      </span>
    </div>
  );
}

// ─── Session Timer ──────────────────────────────────────────
function SessionTimer({ running }: { running: boolean }) {
  const [secs, setSecs] = useState(0);
  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setSecs(s => s + 1), 1000);
    return () => clearInterval(t);
  }, [running]);
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = secs % 60;
  return (
    <div className="flex flex-col items-center">
      <span className="text-[9px] font-black text-stone-600 uppercase tracking-widest mb-0.5">Session</span>
      <span className="text-xs font-mono font-bold text-stone-300 tabular-nums">
        {String(h).padStart(2,'0')}:{String(m).padStart(2,'0')}:{String(s).padStart(2,'0')}
      </span>
    </div>
  );
}

// ─── Settings Modal ─────────────────────────────────────────
function SettingsModal({ isOpen, onClose, mapping, onSave, baseUrl }: {
  isOpen: boolean; onClose: () => void; mapping: CameraMapping;
  onSave: (m: CameraMapping) => void; baseUrl: string;
}) {
  const [activeTab, setActiveTab] = useState<'camera'|'system'|'display'|'session'>('camera');
  const [localMap, setLocalMap] = useState<CameraMapping>(mapping);
  const [settings, setSettings] = useState<AppSettings>({
    confidence: 0.5, pass_threshold: 85, voice_language: 'en',
    show_skeleton: true, show_id_overlay: true, auto_save_session: false, image_size: 640,
  });
  const [saveStatus, setSaveStatus] = useState<'idle'|'saving'|'saved'|'error'>('idle');

  useEffect(() => {
    if (!isOpen) return;
    setLocalMap(mapping);
    fetch(`${baseUrl}/api/settings`).then(r => r.json()).then(data => {
      setSettings(s => ({ ...s, ...data }));
    }).catch(() => {});
  }, [isOpen, mapping, baseUrl]);

  const handleSave = async () => {
    setSaveStatus('saving');
    try {
      await fetch(`${baseUrl}/api/settings`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...settings, camera_mapping: localMap }),
      });
      onSave(localMap);
      setSaveStatus('saved');
      setTimeout(() => { setSaveStatus('idle'); onClose(); }, 800);
    } catch { setSaveStatus('error'); setTimeout(() => setSaveStatus('idle'), 2000); }
  };

  if (!isOpen) return null;

  const tabs = [
    { id: 'camera' as const, label: 'Camera', icon: '📷' },
    { id: 'system' as const, label: 'System', icon: '⚙️' },
    { id: 'display' as const, label: 'Display', icon: '🖥️' },
    { id: 'session' as const, label: 'Session', icon: '📋' },
  ];

  const SliderRow = ({ label, desc, min, max, step, value, onChange }: { label: string; desc: string; min: number; max: number; step: number; value: number; onChange: (v: number) => void; }) => (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-1">
        <label className="text-sm font-bold text-stone-200 uppercase tracking-widest">{label}</label>
        <span className="text-sm font-mono text-stone-300 bg-stone-800 px-2 py-0.5 rounded">{value}</span>
      </div>
      <p className="text-xs text-stone-500 mb-2">{desc}</p>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="w-full h-1.5 bg-stone-700 rounded-full appearance-none cursor-pointer accent-stone-300" />
      <div className="flex justify-between text-[10px] text-stone-600 mt-1"><span>{min}</span><span>{max}</span></div>
    </div>
  );

  const ToggleRow = ({ label, desc, value, onChange }: { label: string; desc: string; value: boolean; onChange: (v: boolean) => void; }) => (
    <div className="flex items-center justify-between mb-4 p-4 bg-stone-800/50 rounded-xl border border-white/5">
      <div>
        <div className="text-sm font-bold text-stone-200 uppercase tracking-widest">{label}</div>
        <div className="text-xs text-stone-500 mt-0.5">{desc}</div>
      </div>
      <button onClick={() => onChange(!value)} className={`relative w-12 h-6 rounded-full transition-colors shrink-0 ${value ? 'bg-stone-300' : 'bg-stone-700'}`}>
        <span className={`absolute top-1 w-4 h-4 rounded-full bg-stone-950 transition-all ${value ? 'left-7' : 'left-1'}`} />
      </button>
    </div>
  );

  const SelectRow = ({ label, desc, value, options, onChange }: { label: string; desc: string; value: string|number; options: {value: string|number; label: string}[]; onChange: (v: string) => void; }) => (
    <div className="mb-5">
      <label className="text-sm font-bold text-stone-200 uppercase tracking-widest">{label}</label>
      <p className="text-xs text-stone-500 mt-0.5 mb-2">{desc}</p>
      <select value={value} onChange={e => onChange(e.target.value)}
        className="w-full bg-stone-800 border border-stone-700 text-stone-200 text-sm rounded-lg px-3 py-2 outline-none focus:border-stone-500">
        {options.map(o => <option key={String(o.value)} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center">
      <div className="absolute inset-0 bg-stone-950/80 backdrop-blur-md" onClick={onClose} />
      <motion.div initial={{ opacity: 0, scale: 0.97, y: 10 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ duration: 0.2 }}
        className="relative w-full max-w-2xl mx-6 bg-stone-900/98 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
        {/* Accent bar */}
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-stone-400/50 to-transparent" />
        <div className="flex items-center justify-between px-8 py-5 border-b border-white/5">
          <div className="flex items-center gap-3">
            <img src="/top_right_logo.png" alt="SDD" className="w-10 h-10 object-contain" />
            <div>
              <h2 className="text-lg font-black text-stone-100 tracking-wide uppercase">System Settings</h2>
              <p className="text-xs text-stone-500 mt-0.5">Military Drill Analysis System · SDD, MCEME</p>
            </div>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full bg-stone-800 hover:bg-stone-700 flex items-center justify-center text-stone-400 hover:text-stone-200 transition-colors text-xl leading-none">×</button>
        </div>
        <div className="flex border-b border-white/5 px-6 pt-2">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2.5 text-xs font-bold uppercase tracking-widest mr-2 border-b-2 transition-colors ${activeTab === t.id ? 'text-stone-100 border-stone-300 bg-stone-800/50 rounded-t' : 'text-stone-500 border-transparent hover:text-stone-300'}`}>
              {t.icon} {t.label}
            </button>
          ))}
        </div>
        <div className="px-8 py-6 max-h-[50vh] overflow-y-auto">
          {activeTab === 'camera' && (
            <div>
              <p className="text-xs text-stone-500 mb-5 uppercase tracking-widest">Map physical camera indices to their position relative to the drill subject.</p>
              {(['front', 'side', 'back'] as (keyof CameraMapping)[]).map(field => (
                <div key={field} className="flex items-center justify-between mb-4 p-4 bg-stone-800/50 rounded-xl border border-white/5">
                  <div>
                    <div className="text-sm font-bold text-stone-200 uppercase tracking-widest">{field} Camera</div>
                    <div className="text-xs text-stone-500 mt-0.5">{field==='front'?'Primary evaluation view':field==='side'?'Lateral posture view':'Rear alignment view'}</div>
                  </div>
                  <div className="flex gap-2">
                    {[0,1,2].map(i => (
                      <button key={i} onClick={() => setLocalMap(p => ({ ...p, [field]: i }))}
                        className={`w-10 h-10 rounded-lg font-bold text-sm transition-colors ${localMap[field]===i?'bg-stone-300 text-stone-950':'bg-stone-700 text-stone-300 hover:bg-stone-600'}`}>
                        {i}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
          {activeTab === 'system' && (
            <div>
              <SliderRow label="Detection Confidence" desc="Minimum YOLO pose keypoint confidence. Lower = more detections, higher = fewer false positives." min={0.1} max={0.95} step={0.05} value={settings.confidence} onChange={v => setSettings(s => ({...s,confidence:v}))} />
              <SliderRow label="Pass Score Threshold (%)" desc="Minimum overall score to receive a PASS verdict." min={50} max={100} step={5} value={settings.pass_threshold} onChange={v => setSettings(s => ({...s,pass_threshold:v}))} />
              <SelectRow label="Image Size" desc="Frame resolution for pose inference." value={settings.image_size}
                options={[{value:320,label:'320px (Fast)'},{value:480,label:'480px'},{value:640,label:'640px (Default)'},{value:1280,label:'1280px (Accurate)'}]}
                onChange={v => setSettings(s => ({...s,image_size:Number(v)}))} />
              <SelectRow label="Voice Language" desc="Language hint for Whisper speech-to-text." value={settings.voice_language}
                options={[{value:'en',label:'English'},{value:'hi',label:'Hindi'},{value:'auto',label:'Auto-detect'}]}
                onChange={v => setSettings(s => ({...s,voice_language:v}))} />
            </div>
          )}
          {activeTab === 'display' && (
            <div className="space-y-2">
              <ToggleRow label="Show ID Overlay" desc="Display detected cadet track IDs on camera feed." value={settings.show_id_overlay} onChange={v => setSettings(s => ({...s,show_id_overlay:v}))} />
              <ToggleRow label="Show Skeleton Overlay" desc="Draw pose skeleton lines on live camera feed." value={settings.show_skeleton} onChange={v => setSettings(s => ({...s,show_skeleton:v}))} />
            </div>
          )}
          {activeTab === 'session' && (
            <div>
              <ToggleRow label="Auto-Save Session" desc="Automatically save results when ending a session." value={settings.auto_save_session} onChange={v => setSettings(s => ({...s,auto_save_session:v}))} />
              <div className="mt-4 p-5 bg-stone-800/50 rounded-xl border border-white/5">
                <div className="text-xs text-stone-500 uppercase tracking-widest mb-3">About this Build</div>
                <div className="text-stone-200 text-sm font-semibold">Military Drill Analysis System</div>
                <div className="text-stone-500 text-xs mt-1">Simulation Development Division (SDD), MCEME</div>
                <div className="mt-3 pt-3 border-t border-white/5">
                  <div className="text-stone-500 text-xs">Developed by <span className="text-stone-300 font-medium">Janardhan & Shankumar</span></div>
                  <div className="text-stone-500 text-xs mt-1">Under the guidance of <span className="text-stone-300 font-medium">Lt Col K Srinath</span></div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="flex items-center justify-between px-8 py-4 border-t border-white/5 bg-stone-950/40">
          <span className="text-xs text-stone-600">Changes are applied live to the backend</span>
          <div className="flex gap-3">
            <button onClick={onClose} className="px-5 py-2 text-sm bg-stone-800 hover:bg-stone-700 text-stone-300 rounded-lg font-bold uppercase tracking-wider">Cancel</button>
            <button onClick={handleSave} disabled={saveStatus==='saving'}
              className={`px-6 py-2 text-sm rounded-lg font-bold uppercase tracking-wider transition-all ${saveStatus==='saved'?'bg-emerald-600 text-white':saveStatus==='error'?'bg-red-600 text-white':'bg-stone-200 text-stone-950 hover:bg-white'}`}>
              {saveStatus==='saving'?'Saving...':saveStatus==='saved'?'✓ Saved':saveStatus==='error'?'Error!':'Save Settings'}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// ─── Launch Screen ──────────────────────────────────────────
function LaunchScreen({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    const bootSequence = [
      "Initializing core neural matrix...",
      "Loading pose estimation models...",
      "Calibrating multi-camera telemetry...",
      "Establishing secure WebSocket streams...",
      "System Ready."
    ];
    let step = 0;
    const interval = setInterval(() => {
      setProgress(prev => { const next = prev + (100/bootSequence.length); if (next >= 100) clearInterval(interval); return next; });
      setLogs(prev => [...prev, bootSequence[step]]);
      step++;
      if (step >= bootSequence.length) setTimeout(onComplete, 1200);
    }, 600);
    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <>
      <div className="fixed top-8 left-8 z-[100] pointer-events-none">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-16 lg:w-20 h-auto object-contain drop-shadow-md" />
      </div>
      <motion.div className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden font-sans"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, scale: 1.05 }} transition={{ duration: 0.8 }}>
        <div className="absolute inset-0 z-0 pointer-events-none">
          <img src="/hello.jpg" alt="Background" className="w-full h-full object-cover blur-md scale-105" />
          <div className="absolute inset-0 bg-black/20" />
          <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
            <h1 className="text-[10rem] lg:text-[18rem] font-black font-sans tracking-tighter text-white/5 select-none whitespace-nowrap">INDIAN ARMY</h1>
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

// ─── Onboarding Screen ──────────────────────────────────────
function OnboardingScreen({ onNext }: { onNext: () => void }) {
  return (
    <>
      <div className="fixed top-8 left-8 z-[100] pointer-events-none">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-16 lg:w-20 h-auto object-contain drop-shadow-md" />
      </div>
      <motion.div className="fixed inset-0 z-40 flex items-center justify-center overflow-hidden"
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, x: -50, filter: "blur(10px)" }} transition={{ duration: 0.8, ease: "easeOut" }}>
        <div className="absolute inset-0 z-0 pointer-events-none">
          <img src="/hello2.jpg" alt="Background" className="w-full h-full object-cover blur-md scale-105" />
          <div className="absolute inset-0 bg-black/20" />
          <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
            <h1 className="text-[10rem] lg:text-[18rem] font-black font-sans tracking-tighter text-white/5 select-none whitespace-nowrap opacity-50">INDIAN ARMY</h1>
          </div>
        </div>
        <div className="absolute inset-0 pointer-events-none z-0">
          <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '40px 40px' }} />
        </div>
        <div className="bg-stone-900/40 backdrop-blur-3xl shadow-2xl border border-white/5 p-12 lg:p-16 rounded-[2.5rem] max-w-7xl w-full mx-6 relative z-10 overflow-hidden">
          <img src="/hello.jpg" alt="Hero Graphic" className="absolute top-0 right-0 w-[300px] lg:w-[450px] h-auto object-contain opacity-40 rounded-bl-[100px] mix-blend-luminosity" />
          <motion.div className="relative z-10" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 1, ease: "easeOut" }}>
            <div className="flex items-center space-x-4 mb-6">
              <img src="/logo.jpeg" alt="Logo" className="w-10 h-10 object-cover rounded-full shadow-lg border border-white/10 mix-blend-luminosity" />
              <h3 className="text-xs font-bold text-stone-400 tracking-[0.4em] uppercase opacity-90">Simulation Development Division (SDD), MCEME</h3>
            </div>
            <h1 className="text-5xl lg:text-[5.5rem] font-black text-stone-100 tracking-tighter mb-8 leading-[1.05] drop-shadow-md">
              Military Drill <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-stone-400 via-stone-300 to-stone-500">Analysis System.</span>
            </h1>
            <div className="flex items-center space-x-4 mb-10">
              <div className="w-32 h-[2px] bg-gradient-to-r from-stone-500 to-stone-400 rounded-full" />
              <div className="w-4 h-[2px] bg-stone-400 rounded-full" />
              <div className="w-2 h-[2px] bg-stone-400 rounded-full opacity-50" />
            </div>
            <p className="text-lg lg:text-xl text-stone-400 max-w-3xl leading-relaxed mb-14 font-medium">
              A professional evaluation suite designed for rigorous posture and alignment tracking.
              Initialize the workspace to begin real-time, multi-camera drill compliance assessment powered by state-of-the-art neural engines.
            </p>
            <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mt-4">
              <div className="flex flex-col space-y-2 text-stone-400">
                <p className="text-sm tracking-wide font-medium">
                  <span className="text-stone-300 font-bold uppercase tracking-widest text-xs mr-2">Project By:</span>Janardhan &amp; Shankumar
                </p>
                <p className="text-xs tracking-wider uppercase font-bold opacity-70">
                  Under the Guidance &amp; Mentorship of <span className="text-stone-300">Lt Col K Srinath</span>
                </p>
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

// ─── Countdown Screen ───────────────────────────────────────
function CountdownScreen({ onComplete }: { onComplete: () => void }) {
  const [count, setCount] = useState(5);
  useEffect(() => {
    if (count > 0) { const t = setTimeout(() => setCount(count - 1), 1000); return () => clearTimeout(t); }
    else { const t = setTimeout(onComplete, 800); return () => clearTimeout(t); }
  }, [count, onComplete]);
  return (
    <motion.div className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="absolute inset-0">
        <img src="/hello2.jpg" alt="bg" className="w-full h-full object-cover blur-lg scale-110 opacity-30" />
        <div className="absolute inset-0 bg-stone-950/80" />
      </div>
      <div className="fixed top-8 left-8 z-[100]">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-16 h-auto object-contain drop-shadow-md" />
      </div>
      <AnimatePresence mode="wait">
        <motion.div key={count} initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 1.5, opacity: 0 }} transition={{ duration: 0.5 }}
          className="text-[12rem] font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-stone-100 to-stone-500 relative z-10 select-none">
          {count > 0 ? count : "GO"}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
}

// ─── Telemetry Card ─────────────────────────────────────────
function TelemetryGaugeCard({ label, value, index }: { label: string; value: any; index: number }) {
  if (typeof value === "number") return null;
  const isPass = value.status === "pass";
  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}
      className={`p-3.5 rounded-xl border transition-all group ${isPass ? 'border-emerald-500/20 bg-emerald-950/20 hover:border-emerald-500/40 hover:bg-emerald-950/30' : 'border-red-500/20 bg-red-950/10 hover:border-red-500/40 hover:bg-red-950/20'}`}>
      <div className="flex items-start justify-between mb-2">
        <h4 className="text-[10px] font-black text-stone-300 tracking-wider uppercase leading-tight flex-1 mr-2">{label}</h4>
        <div className={`shrink-0 flex items-center gap-1 text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest ${isPass ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
          <span className={`w-1 h-1 rounded-full ${isPass ? 'bg-emerald-400' : 'bg-red-400'}`} />
          {isPass ? 'PASS' : 'FAIL'}
        </div>
      </div>
      <div className="text-[10px] text-stone-500 font-mono leading-relaxed">{value.reason}</div>
      {/* Mini progress bar */}
      <div className="mt-2 h-0.5 w-full bg-stone-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${isPass ? 'bg-emerald-500/60 w-full' : 'bg-red-500/60 w-2/3'}`} />
      </div>
    </motion.div>
  );
}

// ─── HUD Corner Brackets ────────────────────────────────────
function HUDCorners({ color = "stone" }: { color?: string }) {
  const cls = `absolute w-5 h-5 border-stone-500/50`;
  return (
    <>
      <span className={`${cls} top-3 left-3 border-t border-l`} />
      <span className={`${cls} top-3 right-3 border-t border-r`} />
      <span className={`${cls} bottom-3 left-3 border-b border-l`} />
      <span className={`${cls} bottom-3 right-3 border-b border-r`} />
    </>
  );
}

// ─── Score Ring ─────────────────────────────────────────────
function ScoreRing({ score, isPass, isInitializing }: { score: number; isPass: boolean; isInitializing: boolean }) {
  const radius = 38;
  const circ = 2 * Math.PI * radius;
  const offset = circ - (score / 100) * circ;
  const color = isInitializing ? '#57534e' : isPass ? '#34d399' : '#f87171';

  return (
    <div className="relative w-28 h-28 flex items-center justify-center">
      <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={radius} fill="none" stroke="#292524" strokeWidth="6" />
        <motion.circle cx="50" cy="50" r={radius} fill="none" stroke={color} strokeWidth="6"
          strokeLinecap="round" strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: "easeOut" }} />
      </svg>
      <div className="relative z-10 text-center">
        <div className="text-2xl font-black tabular-nums" style={{ color }}>{isInitializing ? '—' : `${score}%`}</div>
        <div className="text-[8px] font-bold text-stone-600 uppercase tracking-widest mt-0.5">Overall</div>
      </div>
    </div>
  );
}

// ─── Dashboard ──────────────────────────────────────────────
import { globalCadetTracker } from "@/utils/CadetTracker";

function Dashboard({ onComplete }: { onComplete: (results: any[]) => void }) {
  const BASE_URL = "http://localhost:8000";
  const defaultMapping: CameraMapping = { front: 0, side: 1, back: 2 };
  const [cameraMap, setCameraMap] = useState<CameraMapping>(defaultMapping);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [selectedCam, setSelectedCam] = useState<number>(0);
  const [selectedCadet, setSelectedCadet] = useState<string | null>(null);
  const [sessionResults, setSessionResults] = useState<{ drill: string, pass: boolean, score: number }[]>([]);
  const [wsStatus, setWsStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  const [telemetry, setTelemetry] = useState<{ metrics: Record<string, any>; overall_score: number; status: string; detected_ids: number[]; active_mode?: string; last_command?: string; }>({
    metrics: {}, overall_score: 0, status: "Initializing...", detected_ids: [], active_mode: "SAVDHAN", last_command: ""
  });
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("cameraMapping");
      if (saved) { const parsed = JSON.parse(saved); setCameraMap(parsed); setSelectedCam(parsed.front); }
    } catch {}
  }, []);

  const persistMapping = (map: CameraMapping) => {
    localStorage.setItem("cameraMapping", JSON.stringify(map));
    setCameraMap(map); setSelectedCam(map.front);
  };

  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/telemetry`);
    wsRef.current = ws;
    ws.onopen = () => setWsStatus("connected");
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { overall_score, status, detected_ids, active_mode, last_command, ...metrics } = data;
        const cleanMetrics: Record<string, any> = {};
        for (const key in metrics) {
          if (metrics[key] && metrics[key].status !== "not_evaluable") {
            const formattedKey = key.split('_').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            cleanMetrics[formattedKey] = metrics[key];
          }
        }
        setTelemetry({ metrics: cleanMetrics, overall_score: overall_score || 0, status: status || "Initializing...", detected_ids: detected_ids || [], active_mode: active_mode || "SAVDHAN", last_command: last_command || "" });
      } catch {}
    };
    ws.onclose = () => { setWsStatus("disconnected"); reconnectTimeout.current = setTimeout(connectWebSocket, 3000); };
    ws.onerror = () => ws.close();
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => { if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current); wsRef.current?.close(); };
  }, [connectWebSocket]);

  const changeMode = (mode: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send(JSON.stringify({ mode }));
  };

  const lockCadet = async (id: number) => {
    setSelectedCadet(id.toString());
    try { await fetch(`${BASE_URL}/api/lock_cadet`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ track_id: id }) }); }
    catch {}
  };

  const saveSession = () => {
    const isP = telemetry.overall_score >= 80;
    const newResults = [...sessionResults, { drill: telemetry.active_mode || "SAVDHAN", pass: isP, score: telemetry.overall_score }];
    setSessionResults(newResults);
    onComplete(newResults);
  };

  const isPass = ['Excellent','Good','PASS'].includes(telemetry.status);
  const isInitializing = telemetry.status === "Initializing...";

  const drillModes = [
    { label: "Savadhan", val: "SAVDHAN", short: "SVD" },
    { label: "Vishram", val: "VISHRAM", short: "VSH" },
    { label: "Salute", val: "FRONT_SALUTE", short: "SLT" },
    { label: "Aaram Se", val: "AARAM_SE", short: "ARM" },
  ];

  const camPositions = ['front','side','back'] as (keyof CameraMapping)[];

  return (
    <motion.div className="h-screen w-full flex flex-col font-sans bg-stone-950 text-stone-100 overflow-hidden relative"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6 }}>

      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} mapping={cameraMap} onSave={persistMapping} baseUrl={BASE_URL} />

      {/* Ambient Background */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <img src="/hello2.jpg" alt="bg" className="w-full h-full object-cover blur-2xl scale-110 opacity-10" />
        <div className="absolute inset-0 bg-stone-950/95" />
        <div className="absolute inset-0 opacity-[0.025]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '32px 32px' }} />
      </div>

      {/* ── Header ─────────────────────────────────────────── */}
      <header className="h-14 flex items-center justify-between px-5 lg:px-6 border-b border-white/[0.06] bg-stone-900/70 backdrop-blur-xl relative z-40 shrink-0">
        {/* Left brand */}
        <div className="flex items-center gap-3">
          <img src="/top_right_logo.png" alt="SDD" className="w-8 h-8 object-contain" />
          <div>
            <div className="text-[11px] font-black tracking-[0.15em] uppercase text-stone-100 leading-none">Military Drill <span className="text-stone-500 font-normal">Analysis System</span></div>
            <div className="text-[8px] font-bold tracking-[0.3em] text-stone-700 uppercase mt-0.5">SDD · MCEME · REAL-TIME</div>
          </div>
        </div>

        {/* Center: Mode Selector */}
        <div className="hidden lg:flex items-center gap-1 bg-stone-900 border border-white/[0.06] rounded-full p-1">
          {drillModes.map(m => (
            <button key={m.val} onClick={() => changeMode(m.val)}
              className={`px-4 py-1.5 text-[10px] font-black tracking-widest uppercase rounded-full transition-all duration-200 ${telemetry.active_mode === m.val ? 'bg-stone-200 text-stone-950 shadow-sm' : 'text-stone-600 hover:text-stone-300'}`}>
              {m.label}
            </button>
          ))}
        </div>

        {/* Right */}
        <div className="flex items-center gap-3">
          <SessionTimer running={wsStatus === 'connected'} />
          <div className="w-px h-6 bg-white/5" />
          <LiveClock />
          <div className="w-px h-6 bg-white/5" />

          {/* Connection */}
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-[9px] font-black uppercase tracking-widest transition-colors ${wsStatus==='connected'?'border-emerald-500/30 bg-emerald-950/30 text-emerald-400':'border-red-500/30 bg-red-950/30 text-red-400'}`}>
            {wsStatus==='connected'?<Wifi className="w-3 h-3"/>:<WifiOff className="w-3 h-3"/>}
            {wsStatus}
          </div>

          <button onClick={() => setIsSettingsOpen(true)} className="p-2 bg-stone-800/80 hover:bg-stone-700 border border-white/[0.06] rounded-lg text-stone-500 hover:text-stone-200 transition-colors">
            <Settings className="w-3.5 h-3.5" />
          </button>
          <button onClick={saveSession} className="flex items-center gap-2 px-4 py-2 bg-stone-800 hover:bg-stone-700 border border-white/[0.06] text-stone-400 hover:text-stone-200 rounded-lg text-[10px] font-black uppercase tracking-wider transition-colors">
            <LogOut className="w-3 h-3" />End Session
          </button>
        </div>
      </header>

      {/* ── Main ──────────────────────────────────────────── */}
      <main className="flex-1 p-3 lg:p-4 overflow-hidden flex gap-3 relative z-10 min-h-0">

        {/* Camera Sidebar */}
        <div className="w-48 xl:w-52 flex flex-col gap-3 shrink-0">
          {camPositions.map((pos, idx) => {
            const camId = cameraMap[pos];
            const isSelected = selectedCam === camId;
            return (
              <motion.div key={pos} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.1 }}
                onClick={() => setSelectedCam(camId)}
                className={`flex-1 relative rounded-xl overflow-hidden cursor-pointer border transition-all duration-200 group ${isSelected ? 'border-stone-400/60 shadow-[0_0_24px_rgba(120,113,108,0.15)]' : 'border-white/[0.06] hover:border-stone-600/60'}`}>

                {/* Camera header bar */}
                <div className={`absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-2.5 py-1.5 ${isSelected ? 'bg-stone-950/80' : 'bg-stone-950/60'} backdrop-blur-sm border-b border-white/[0.06]`}>
                  <span className="text-[8px] font-black tracking-[0.2em] text-stone-300 uppercase">{pos}</span>
                  <div className="flex items-center gap-1">
                    <span className={`w-1.5 h-1.5 rounded-full ${isSelected ? 'bg-red-500 animate-pulse' : 'bg-stone-700'}`} />
                    <span className="text-[7px] font-mono text-stone-600">C{camId}</span>
                  </div>
                </div>

                <img src={`http://localhost:8000/api/video_feed/${camId}`} alt={pos}
                  className={`w-full h-full object-cover mt-7 transition-all ${isSelected ? 'opacity-100' : 'opacity-40 group-hover:opacity-70'}`}
                  onError={e => { e.currentTarget.style.display = 'none'; }} />
                <div className="absolute inset-0 mt-7 flex flex-col items-center justify-center pointer-events-none">
                  <Activity className="w-4 h-4 text-stone-800 mb-1" />
                  <span className="text-[7px] font-bold tracking-widest uppercase text-stone-800">No Signal</span>
                </div>

                {/* HUD corners */}
                <div className="absolute top-7 left-1.5 w-3 h-3 border-t border-l border-stone-600/50" />
                <div className="absolute top-7 right-1.5 w-3 h-3 border-t border-r border-stone-600/50" />
                <div className="absolute bottom-1.5 left-1.5 w-3 h-3 border-b border-l border-stone-600/50" />
                <div className="absolute bottom-1.5 right-1.5 w-3 h-3 border-b border-r border-stone-600/50" />

                {isSelected && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-stone-300/80 to-transparent" />}
              </motion.div>
            );
          })}
        </div>

        {/* Main Camera */}
        <div className="flex-1 relative rounded-2xl overflow-hidden bg-stone-900/50 backdrop-blur-sm border border-white/[0.06] flex flex-col min-w-0">
          {/* Top gradient accent */}
          <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-stone-400/40 to-transparent z-20" />

          {/* Top overlays */}
          <div className="absolute top-3 left-3 z-20 flex items-center gap-2">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-stone-950/80 backdrop-blur border border-white/[0.08] rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
              <span className="text-[9px] font-black tracking-widest text-stone-200 uppercase">
                CAM {selectedCam} · {selectedCam===cameraMap.front?'FRONT':selectedCam===cameraMap.side?'SIDE':'BACK'}
              </span>
            </div>
            {telemetry.active_mode && (
              <div className="px-3 py-1.5 bg-stone-950/80 backdrop-blur border border-stone-600/30 rounded-full text-[9px] font-black text-stone-300 uppercase tracking-widest">
                ◆ {telemetry.active_mode}
              </div>
            )}
          </div>

          {/* Mobile mode row */}
          <div className="lg:hidden absolute top-3 right-3 z-20 flex gap-1.5">
            {drillModes.map(m => (
              <button key={m.val} onClick={() => changeMode(m.val)}
                className={`px-2 py-1 text-[8px] font-black uppercase tracking-widest rounded-full transition-all ${telemetry.active_mode===m.val?'bg-stone-200 text-stone-950':'bg-stone-900/80 border border-white/[0.06] text-stone-500'}`}>
                {m.short}
              </button>
            ))}
          </div>

          {/* Video */}
          <div className="w-full h-full relative flex items-center justify-center bg-stone-950/20">
            <img src={`http://localhost:8000/api/video_feed/${selectedCam}`} alt="Feed"
              className="w-full h-full object-contain"
              onError={e => { e.currentTarget.style.display = 'none'; }} />

            {/* HUD overlay - corner brackets */}
            <div className="absolute inset-6 pointer-events-none">
              <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-stone-500/40" />
              <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-stone-500/40" />
              <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-stone-500/40" />
              <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-stone-500/40" />
            </div>

            {/* Targeting reticle when no cadet */}
            {!selectedCadet && selectedCam === cameraMap.front && (
              <div className="absolute inset-0 z-30 flex flex-col items-center justify-center pointer-events-none">
                {/* Pulsing rings */}
                <div className="relative mb-6">
                  <motion.div animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0, 0.3] }} transition={{ duration: 2, repeat: Infinity }}
                    className="absolute inset-0 -m-4 rounded-full border border-stone-500/40" />
                  <div className="w-16 h-16 rounded-full border border-stone-600/60 flex items-center justify-center">
                    <Crosshair className="w-6 h-6 text-stone-600" />
                  </div>
                </div>
                <p className="text-[11px] font-black text-stone-400 uppercase tracking-[0.3em] mb-5">Awaiting Target Acquisition</p>
                <div className="flex gap-3 pointer-events-auto">
                  {telemetry.detected_ids?.length > 0 ? (
                    telemetry.detected_ids.map(id => (
                      <button key={id} onClick={() => lockCadet(id)}
                        className="flex items-center gap-2 px-5 py-2 bg-stone-800/90 border border-stone-600/50 text-stone-200 rounded-full font-black text-[10px] uppercase tracking-widest hover:bg-stone-700/90 transition-all">
                        <Target className="w-3.5 h-3.5" />Lock ID {id}
                      </button>
                    ))
                  ) : (
                    <div className="text-stone-700 font-mono text-[10px] uppercase tracking-widest animate-pulse">Scanning environment...</div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Bottom info strip */}
          <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-stone-950/80 to-transparent z-10 flex items-end px-4 pb-2">
            <div className="flex items-center gap-4 text-[8px] font-mono text-stone-700 uppercase tracking-widest">
              <span>MJPEG STREAM</span>
              <span>·</span>
              <span>30 FPS</span>
              <span>·</span>
              <span>YOLO11n-POSE</span>
              {selectedCadet && <><span>·</span><span className="text-stone-400">LOCKED: ID-{selectedCadet}</span></>}
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="w-72 xl:w-80 shrink-0 flex flex-col gap-3 h-full min-h-0">

          {/* Score Ring + Status */}
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            className="bg-stone-900/60 backdrop-blur-sm border border-white/[0.06] rounded-2xl p-4 shrink-0 relative overflow-hidden">
            <div className={`absolute top-0 left-0 right-0 h-0.5 transition-colors ${isInitializing?'bg-stone-700':isPass?'bg-emerald-400':'bg-red-500'}`} />

            <div className="flex items-center justify-between mb-3">
              <h3 className="text-[9px] font-black tracking-[0.25em] text-stone-600 uppercase">Live Evaluation</h3>
              <div className={`text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest ${wsStatus==='connected'?'bg-emerald-950/50 text-emerald-500':'bg-stone-800 text-stone-600'}`}>
                {wsStatus==='connected'?'● LIVE':'○ OFFLINE'}
              </div>
            </div>

            {/* Score Ring + Status */}
            <div className="flex items-center gap-4 mb-3">
              <ScoreRing score={telemetry.overall_score} isPass={isPass} isInitializing={isInitializing} />
              <div className="flex-1">
                <div className="text-[8px] text-stone-600 uppercase tracking-widest mb-1">Verdict</div>
                <div className={`text-xl font-black uppercase tracking-wide ${isInitializing?'text-stone-600':isPass?'text-emerald-400':'text-red-400'}`}>
                  {isInitializing?'WAITING':isPass?'PASS':'FAIL'}
                </div>
                <div className="text-[8px] text-stone-600 uppercase tracking-widest mt-2 mb-0.5">Target</div>
                <div className="text-xs font-bold text-stone-300">{selectedCadet?`ID-${selectedCadet}`:'Unassigned'}</div>
                <div className="text-[8px] text-stone-600 uppercase tracking-widest mt-1.5 mb-0.5">Mode</div>
                <div className="text-xs font-bold text-stone-300">{telemetry.active_mode||'—'}</div>
              </div>
            </div>

            {/* Score bar */}
            {!isInitializing && (
              <div>
                <div className="h-1 bg-stone-800 rounded-full overflow-hidden">
                  <motion.div className={`h-full rounded-full ${isPass?'bg-emerald-400':'bg-red-500'}`}
                    initial={{ width: 0 }} animate={{ width: `${telemetry.overall_score}%` }} transition={{ duration: 0.8 }} />
                </div>
                <div className="flex justify-between text-[8px] font-mono text-stone-700 mt-1">
                  <span>0</span><span>THRESHOLD</span><span>100</span>
                </div>
              </div>
            )}
          </motion.div>

          {/* Telemetry */}
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
            className="flex-1 min-h-0 bg-stone-900/60 backdrop-blur-sm border border-white/[0.06] rounded-2xl p-4 flex flex-col">
            <div className="flex items-center justify-between mb-3 shrink-0">
              <h3 className="text-[9px] font-black tracking-[0.25em] text-stone-600 uppercase flex items-center gap-2">
                <BarChart3 className="w-3 h-3" />Diagnostic Breakdown
              </h3>
              {Object.keys(telemetry.metrics).length > 0 && (
                <span className="text-[8px] font-mono text-stone-700">{Object.keys(telemetry.metrics).length} metrics</span>
              )}
            </div>
            <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
              {Object.keys(telemetry.metrics).length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full py-8 gap-3">
                  <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ duration: 2, repeat: Infinity }}>
                    <Activity className="w-8 h-8 text-stone-800" />
                  </motion.div>
                  <span className="text-[9px] text-stone-700 uppercase tracking-widest font-bold">Awaiting data stream...</span>
                </div>
              ) : (
                Object.entries(telemetry.metrics).map(([label, value], i) => (
                  <TelemetryGaugeCard key={label} label={label} value={value} index={i} />
                ))
              )}
            </div>
          </motion.div>
        </div>
      </main>

      {/* ── Bottom Status Bar ───────────────────────────────── */}
      <div className="h-7 shrink-0 border-t border-white/[0.04] bg-stone-900/60 backdrop-blur flex items-center justify-between px-5 relative z-20">
        <div className="flex items-center gap-5 text-[8px] font-mono text-stone-700 uppercase tracking-widest">
          <span className={wsStatus==='connected'?'text-emerald-700':'text-red-900'}>● WS {wsStatus}</span>
          <span>· YOLO11n-POSE · BYTETRACK</span>
          <span>· SDD MCEME</span>
        </div>
        <div className="flex items-center gap-5 text-[8px] font-mono text-stone-700 uppercase tracking-widest">
          <span>Janardhan &amp; Shankumar</span>
          <span>·</span>
          <span>Lt Col K Srinath</span>
        </div>
      </div>
    </motion.div>
  );
}

// ─── Results Screen ─────────────────────────────────────────
function ResultsScreen({ results, onRestart }: { results: any[]; onRestart: () => void }) {
  const passed = results.filter(r => r.pass).length;
  const total = results.length;

  return (
    <motion.div className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="absolute inset-0">
        <img src="/hello2.jpg" alt="bg" className="w-full h-full object-cover blur-lg scale-110 opacity-20" />
        <div className="absolute inset-0 bg-stone-950/92" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '40px 40px' }} />
      </div>
      <div className="fixed top-8 left-8 z-[100]">
        <img src="/top_right_logo.png" alt="SDD Logo" className="w-16 h-auto object-contain" />
      </div>
      <div className="relative z-10 w-full max-w-3xl mx-6 p-8 bg-stone-900/80 backdrop-blur-3xl border border-white/10 rounded-3xl shadow-2xl">
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-stone-400/50 to-transparent rounded-t-3xl" />
        <div className="text-center mb-8">
          <div className="text-[9px] font-black tracking-[0.3em] text-stone-600 uppercase mb-2">Session Complete</div>
          <h1 className="text-3xl font-black text-stone-100 uppercase tracking-wider">Final Evaluation</h1>
        </div>
        <div className="grid grid-cols-3 gap-4 mb-8 text-center">
          {[{label:'Total',value:total,color:'text-stone-200'},{label:'Passed',value:passed,color:'text-emerald-400'},{label:'Failed',value:total-passed,color:'text-red-400'}].map(item => (
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
                <span className="text-stone-700 font-mono font-bold text-sm">{(i+1).toString().padStart(2,'0')}</span>
                <span className="text-stone-200 font-bold">{r.drill}</span>
              </div>
              <div className="flex items-center gap-5">
                <div className="text-right">
                  <div className="text-[9px] text-stone-600 uppercase tracking-widest">Score</div>
                  <div className="font-mono text-stone-200 font-bold">{r.score}%</div>
                </div>
                <div className={`px-4 py-1.5 rounded-lg font-black text-[10px] uppercase tracking-wider border ${r.pass?'bg-emerald-950/50 text-emerald-400 border-emerald-500/30':'bg-red-950/50 text-red-400 border-red-500/30'}`}>
                  {r.pass?'PASS':'FAIL'}
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="text-center">
          <button onClick={onRestart} className="px-10 py-4 bg-stone-200 text-stone-950 font-black uppercase tracking-widest rounded-full hover:bg-white active:scale-95 transition-all shadow-xl">
            New Session
          </button>
        </div>
      </div>
    </motion.div>
  );
}

// ─── App Entry ──────────────────────────────────────────────
export default function App() {
  const [appState, setAppState] = useState<"launch"|"onboarding"|"countdown"|"dashboard"|"results">("launch");
  const [finalResults, setFinalResults] = useState<any[]>([]);

  return (
    <AnimatePresence mode="wait">
      {appState==="launch" && <LaunchScreen key="launch" onComplete={() => setAppState("onboarding")} />}
      {appState==="onboarding" && <OnboardingScreen key="onboard" onNext={() => setAppState("dashboard")} />}
      {appState==="dashboard" && <Dashboard key="dashboard" onComplete={results => { setFinalResults(results); setAppState("results"); }} />}
      {appState==="results" && <ResultsScreen key="results" results={finalResults} onRestart={() => setAppState("launch")} />}
    </AnimatePresence>
  );
}
