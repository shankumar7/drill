import re

with open("/Users/shankumar/drill/web-ui/src/app/page.tsx", "r") as f:
    content = f.read()

# 1. Update Lucide Imports
content = re.sub(r'import \{ ([^\}]+) \} from "lucide-react";', r'import { \1, Mic } from "lucide-react";', content)

# 2. Remove ConfigScreen
# We can find ConfigScreen from "function ConfigScreen" to just before "function CountdownScreen"
config_pattern = re.compile(r'// ==========================================\n// 3\. CONFIGURATION SCREEN.*?// ==========================================\n// 4\. COUNTDOWN SCREEN', re.DOTALL)
content = config_pattern.sub('// ==========================================\n// 4. COUNTDOWN SCREEN', content)

# 3. Update Dashboard signature and states
content = content.replace(
    "function Dashboard({ activeWorkflow, onComplete }: { activeWorkflow: string[], onComplete: (results: any[]) => void }) {",
    "function Dashboard({ onComplete }: { onComplete: (results: any[]) => void }) {"
)
content = content.replace("const [currentStepIndex, setCurrentStepIndex] = useState(0);", "")

telemetry_old = """const [telemetry, setTelemetry] = useState<{ metrics: Record<string, any>, overall_score: number, status: string, detected_ids: number[] }>({
    metrics: {},
    overall_score: 0,
    status: "Initializing...",
    detected_ids: []
  });"""
telemetry_new = """const [telemetry, setTelemetry] = useState<{ metrics: Record<string, any>, overall_score: number, status: string, detected_ids: number[], active_mode?: string, last_command?: string }>({
    metrics: {},
    overall_score: 0,
    status: "Initializing...",
    detected_ids: [],
    active_mode: "SAVDHAN",
    last_command: ""
  });
  
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append("audio", audioBlob, "command.webm");
        
        try {
          await fetch("http://localhost:8000/api/voice_command", {
            method: "POST",
            body: formData,
          });
        } catch (e) {
          console.error("Voice command error", e);
        }
        
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Mic error", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };"""
content = content.replace(telemetry_old, telemetry_new)

# Update websocket data extraction
ws_old = """const { overall_score, status, detected_ids, ...metrics } = data;"""
ws_new = """const { overall_score, status, detected_ids, active_mode, last_command, ...metrics } = data;"""
content = content.replace(ws_old, ws_new)

set_tel_old = """setTelemetry({
          metrics: cleanMetrics,
          overall_score: overall_score || 0,
          status: status || "Initializing...",
          detected_ids: detected_ids || []
        });"""
set_tel_new = """setTelemetry({
          metrics: cleanMetrics,
          overall_score: overall_score || 0,
          status: status || "Initializing...",
          detected_ids: detected_ids || [],
          active_mode: active_mode || "SAVDHAN",
          last_command: last_command || ""
        });"""
content = content.replace(set_tel_old, set_tel_new)

# 4. Remove WebSocket active mode sync since Backend decides it now
content = re.sub(r'const rawMode = .*?// 5\. MAIN DASHBOARD \(Multi-Camera\)', r'// 5. MAIN DASHBOARD (Multi-Camera)', content, flags=re.DOTALL)
mode_sync = """const rawMode = activeWorkflow.length > 0 ? activeWorkflow[currentStepIndex].toUpperCase() : "SAVDHAN";
  const modeMap: Record<string, string> = {
    "SAMNE SALUTE": "FRONT_SALUTE",
    "BAYEN SALUTE": "BAYE_SALUTE",
    "DAHINE SALUTE": "DAINE_SALUTE"
  };
  const currentMode = modeMap[rawMode] || rawMode;

  useEffect(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ mode: currentMode }));
    }
  }, [currentMode]);"""
content = content.replace(mode_sync, "")

# 5. Replace "handleNextDrill" usage
handle_next_old = """const handleNextDrill = () => {
    const finalScore = telemetry.overall_score;
    const isPass = finalScore >= 80;
    
    const newResults = [...sessionResults, {
      drill: activeWorkflow[currentStepIndex],
      pass: isPass,
      score: finalScore
    }];
    
    setSessionResults(newResults);

    if (currentStepIndex < activeWorkflow.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1);
      setTelemetry({ metrics: {}, overall_score: 0, status: "Initializing...", detected_ids: [] });
    } else {
      onComplete(newResults);
    }
  };"""
handle_next_new = """const saveSession = () => {
    const finalScore = telemetry.overall_score;
    const isPass = finalScore >= 80;
    
    const newResults = [...sessionResults, {
      drill: telemetry.active_mode || "SAVDHAN",
      pass: isPass,
      score: finalScore
    }];
    
    setSessionResults(newResults);
    onComplete(newResults);
  };"""
content = content.replace(handle_next_old, handle_next_new)

# 6. Update UI in Dashboard
active_drill_old = """<div className="flex flex-col md:flex-row md:items-end justify-between gap-4 shrink-0 mb-4">
              <div>
                <h2 className="text-3xl font-extrabold tracking-tight text-slate-900">Active Drill Session</h2>
                <p className="text-slate-500 mt-1 flex items-center space-x-2">
                  <span>Sequence:</span>
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                  <span className="text-blue-600 font-bold uppercase tracking-wider">
                    {activeWorkflow[currentStepIndex] || "SAVDHAN"}
                  </span>
                  <span className="text-slate-400 font-mono text-xs ml-2">
                    ({currentStepIndex + 1} / {activeWorkflow.length || 1})
                  </span>
                </p>
              </div>
              
            </div>"""

active_drill_new = """<div className="flex flex-col md:flex-row md:items-center justify-between gap-4 shrink-0 mb-4">
              <div>
                <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 flex items-center space-x-3">
                  <span>Active Drill Session</span>
                </h2>
                <p className="text-slate-500 mt-1 flex items-center space-x-2">
                  <span>Mode:</span>
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                  <span className="text-blue-600 font-bold uppercase tracking-wider">
                    {telemetry.active_mode}
                  </span>
                  {telemetry.last_command && (
                    <>
                      <span className="text-slate-300 mx-2">|</span>
                      <span className="text-slate-400 italic font-mono text-xs">Last Command: "{telemetry.last_command}"</span>
                    </>
                  )}
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                <button 
                  onMouseDown={startRecording}
                  onMouseUp={stopRecording}
                  onMouseLeave={stopRecording}
                  onTouchStart={startRecording}
                  onTouchEnd={stopRecording}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-full font-bold shadow-lg transition-all border ${isRecording ? 'bg-red-50 text-red-600 border-red-200 animate-pulse' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'}`}
                >
                  <Mic className={`w-5 h-5 ${isRecording ? 'text-red-500' : 'text-slate-400'}`} />
                  <span>{isRecording ? "Listening..." : "Hold to Speak"}</span>
                </button>
                <button onClick={saveSession} className="px-6 py-3 bg-slate-900 text-white rounded-full font-bold shadow-lg hover:bg-slate-800 transition-colors">
                  End Session
                </button>
              </div>
            </div>"""

content = content.replace(active_drill_old, active_drill_new)


# 7. Update App Component
app_comp_old = """export default function App() {
  const [appState, setAppState] = useState<"launch" | "onboarding" | "config" | "countdown" | "dashboard" | "results">("launch");
  const [workflow, setWorkflow] = useState<string[]>([]);
  const [finalResults, setFinalResults] = useState<any[]>([]);

  return (
    <AnimatePresence mode="wait">
      {appState === "launch" && (
        <LaunchScreen key="launch" onComplete={() => setAppState("onboarding")} />
      )}
      {appState === "onboarding" && (
        <OnboardingScreen key="onboard" onNext={() => setAppState("config")} />
      )}
      {appState === "config" && (
        <ConfigScreen key="config" onStart={(wf) => { setWorkflow(wf); setAppState("dashboard"); }} />
      )}
      {appState === "dashboard" && (
        <Dashboard key="dashboard" activeWorkflow={workflow} onComplete={(results) => { setFinalResults(results); setAppState("results"); }} />
      )}
      {appState === "results" && (
        <ResultsScreen key="results" results={finalResults} onRestart={() => setAppState("launch")} />
      )}
    </AnimatePresence>
  );
}"""

app_comp_new = """export default function App() {
  const [appState, setAppState] = useState<"launch" | "onboarding" | "countdown" | "dashboard" | "results">("launch");
  const [finalResults, setFinalResults] = useState<any[]>([]);

  return (
    <AnimatePresence mode="wait">
      {appState === "launch" && (
        <LaunchScreen key="launch" onComplete={() => setAppState("onboarding")} />
      )}
      {appState === "onboarding" && (
        <OnboardingScreen key="onboard" onNext={() => setAppState("dashboard")} />
      )}
      {appState === "dashboard" && (
        <Dashboard key="dashboard" onComplete={(results) => { setFinalResults(results); setAppState("results"); }} />
      )}
      {appState === "results" && (
        <ResultsScreen key="results" results={finalResults} onRestart={() => setAppState("launch")} />
      )}
    </AnimatePresence>
  );
}"""

content = content.replace(app_comp_old, app_comp_new)

with open("/Users/shankumar/drill/web-ui/src/app/page.tsx", "w") as f:
    f.write(content)
