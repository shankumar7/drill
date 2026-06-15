import re

with open("/Users/shankumar/drill/web-ui/src/app/page.tsx", "r") as f:
    content = f.read()

dashboard_new = """function Dashboard({ onComplete }: { onComplete: (results: any[]) => void }) {
  const [selectedCadet, setSelectedCadet] = useState<string | null>(null);
  const [sessionResults, setSessionResults] = useState<{ drill: string, pass: boolean, score: number }[]>([]);
  const [wsStatus, setWsStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  
  const [telemetry, setTelemetry] = useState<{ metrics: Record<string, any>, overall_score: number, status: string, detected_ids: number[], active_mode?: string, last_command?: string }>({
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
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connectWebSocket = () => {
    const ws = new WebSocket("ws://localhost:8000/ws/telemetry");
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
        
        setTelemetry({
          metrics: cleanMetrics,
          overall_score: overall_score || 0,
          status: status || "Initializing...",
          detected_ids: detected_ids || [],
          active_mode: active_mode || "SAVDHAN",
          last_command: last_command || ""
        });
      } catch (e) {
        console.warn("WebSocket parse error", e);
      }
    };

    ws.onclose = () => {
      setWsStatus("disconnected");
      reconnectTimeout.current = setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = () => ws.close();
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
  }, []);

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
          await fetch("http://localhost:8000/api/voice_command", { method: "POST", body: formData });
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
  };

  const lockCadet = async (id: number) => {
    setSelectedCadet(id.toString());
    try {
      await fetch("http://localhost:8000/api/lock_cadet", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({track_id: id})
      });
    } catch(e) { console.error(e); }
  };

  const saveSession = () => {
    const finalScore = telemetry.overall_score;
    const isPass = finalScore >= 80;
    const newResults = [...sessionResults, {
      drill: telemetry.active_mode || "SAVDHAN",
      pass: isPass,
      score: finalScore
    }];
    setSessionResults(newResults);
    onComplete(newResults);
  };

  // derived status booleans
  const isPass = telemetry.status === 'Excellent' || telemetry.status === 'Good' || telemetry.status === 'PASS';
  const isInitializing = telemetry.status === "Initializing...";

  return (
    <motion.div className="h-screen w-full flex flex-col font-sans bg-[#0B0F19] text-slate-200 overflow-hidden relative" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}>
      
      {/* Background Tech Details */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-blue-600/10 rounded-full blur-[120px] transform translate-x-1/3 -translate-y-1/3"></div>
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-cyan-600/10 rounded-full blur-[120px] transform -translate-x-1/3 translate-y-1/3"></div>
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)`, backgroundSize: '40px 40px' }}></div>
      </div>

      {/* Header */}
      <header className="h-16 flex items-center justify-between px-6 lg:px-8 border-b border-white/10 bg-slate-900/50 backdrop-blur-md relative z-40 shrink-0">
        <div className="flex items-center space-x-4">
          <div className="w-8 h-8 rounded border border-white/20 bg-slate-800 flex items-center justify-center overflow-hidden">
             <Shield className="w-5 h-5 text-blue-400" />
          </div>
          <h1 className="text-sm font-bold tracking-widest uppercase text-slate-100">
            Military Drill <span className="text-blue-500 font-normal">Analysis System</span>
          </h1>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs font-mono">
             <span className={`w-2 h-2 rounded-full ${wsStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></span>
             <span className="text-slate-400 uppercase tracking-widest">{wsStatus}</span>
          </div>
          <button onClick={saveSession} className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded text-xs font-bold uppercase tracking-wider transition-colors flex items-center space-x-2">
            <LogOut className="w-3 h-3" />
            <span>End Session</span>
          </button>
        </div>
      </header>

      {/* Main Grid Content */}
      <main className="flex-1 p-4 lg:p-6 overflow-hidden flex flex-col lg:flex-row gap-6 relative z-10 w-full max-w-[2000px] mx-auto min-h-0">
        
        {/* Left Column: Cameras */}
        <div className="flex-1 flex flex-col min-h-0 gap-6">
          
          {/* Main Camera HUD */}
          <div className="flex-1 min-h-0 relative bg-slate-900/40 rounded-2xl border border-white/10 backdrop-blur-sm overflow-hidden flex flex-col shadow-[0_0_40px_rgba(0,0,0,0.5)]">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-600 via-cyan-400 to-transparent z-20"></div>
            
            <div className="absolute top-4 left-4 z-20 flex items-center space-x-3">
              <div className="px-3 py-1 bg-black/60 backdrop-blur border border-white/10 rounded text-[10px] font-bold text-white tracking-widest uppercase flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                <span>CAM 1: FRONT</span>
              </div>
              {telemetry.active_mode && (
                <div className="px-3 py-1 bg-blue-600/20 backdrop-blur border border-blue-500/30 rounded text-[10px] font-bold text-blue-400 tracking-widest uppercase">
                  MODE: {telemetry.active_mode}
                </div>
              )}
            </div>

            <div className="w-full h-full relative flex items-center justify-center bg-black/50">
              {selectedCadet ? (
                <img 
                  src="http://localhost:8000/api/video_feed/0" 
                  alt="Main Camera Feed" 
                  className="w-full h-full object-contain"
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
              ) : (
                <>
                  <img 
                    src="http://localhost:8000/api/video_feed/0" 
                    alt="Main Camera Feed (Unselected)" 
                    className="w-full h-full object-contain opacity-40 blur-sm"
                    onError={(e) => { e.currentTarget.style.display = 'none'; }}
                  />
                  <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-slate-950/60 backdrop-blur-sm">
                    <div className="w-24 h-24 border border-blue-500/50 rounded-full flex items-center justify-center relative mb-6">
                       <div className="absolute inset-0 border-t-2 border-blue-400 rounded-full animate-spin"></div>
                       <Activity className="w-8 h-8 text-blue-400" />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2 tracking-widest">AWAITING TARGET ACQUISITION</h3>
                    <p className="text-xs text-slate-400 mb-6 font-mono uppercase tracking-widest">Select a detected cadet ID to lock focus</p>
                    <div className="flex gap-3">
                      {telemetry.detected_ids && telemetry.detected_ids.length > 0 ? (
                        telemetry.detected_ids.map(id => (
                          <button
                            key={id}
                            onClick={() => lockCadet(id)}
                            className="px-6 py-2 bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 rounded border border-blue-500/50 font-bold text-xs tracking-widest uppercase transition-colors flex items-center space-x-2"
                          >
                            <Users className="w-4 h-4" />
                            <span>ID: {id}</span>
                          </button>
                        ))
                      ) : (
                        <div className="text-slate-500 font-mono text-xs uppercase tracking-widest animate-pulse">Scanning environment...</div>
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>
            {/* HUD Corner Accents */}
            <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-blue-500/50 pointer-events-none"></div>
            <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-blue-500/50 pointer-events-none"></div>
          </div>

          {/* Secondary Cameras (Horizontal Split) */}
          <div className="h-48 shrink-0 flex gap-6">
            {[
              { id: 1, label: "CAM 2: SIDE" },
              { id: 2, label: "CAM 3: BACK" }
            ].map((cam) => (
              <div key={cam.id} className="flex-1 relative bg-slate-900/40 rounded-xl border border-white/10 backdrop-blur-sm overflow-hidden flex items-center justify-center group">
                <div className="absolute top-2 left-2 z-20 px-2 py-1 bg-black/60 backdrop-blur border border-white/10 rounded text-[9px] font-bold text-slate-300 tracking-widest uppercase">
                  {cam.label}
                </div>
                <img 
                  src={`http://localhost:8000/api/video_feed/${cam.id}`} 
                  alt={cam.label}
                  className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    e.currentTarget.nextElementSibling?.classList.remove('hidden');
                    e.currentTarget.nextElementSibling?.classList.add('flex');
                  }}
                />
                <div className="hidden absolute inset-0 flex flex-col items-center justify-center text-slate-600">
                  <Activity className="w-6 h-6 mb-2 opacity-50" />
                  <span className="text-[10px] font-bold tracking-widest uppercase">NO SIGNAL</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Telemetry & Status */}
        <div className="lg:w-[400px] shrink-0 flex flex-col gap-6 h-full min-h-0">
          
          {/* Status Panel */}
          <div className="bg-slate-900/60 rounded-2xl border border-white/10 backdrop-blur-md p-6 flex flex-col relative overflow-hidden shrink-0">
            <div className={`absolute top-0 left-0 w-full h-1 ${isInitializing ? 'bg-slate-500' : (isPass ? 'bg-emerald-500 shadow-[0_0_20px_#10b981]' : 'bg-red-500 shadow-[0_0_20px_#ef4444]')}`}></div>
            
            <h3 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-4">Live Evaluation Status</h3>
            
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-1">Target Identity</div>
                <div className="font-bold text-slate-200">{selectedCadet ? `CADET ID-${selectedCadet}` : 'UNASSIGNED'}</div>
              </div>
              <div className="text-right">
                <div className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mb-1">System Confidence</div>
                <div className="font-bold text-blue-400">92%</div>
              </div>
            </div>

            <div className={`mt-2 py-4 rounded-xl border flex items-center justify-center space-x-3
              ${isInitializing ? 'bg-slate-800/50 border-slate-700/50 text-slate-400' : 
                (isPass ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400')}`}>
              {isInitializing ? <Activity className="w-6 h-6 animate-pulse" /> : (isPass ? <CheckCircle className="w-6 h-6" /> : <XCircle className="w-6 h-6" />)}
              <span className="text-3xl font-black uppercase tracking-widest drop-shadow-md">
                {isInitializing ? "WAITING" : (isPass ? "PASS" : "FAIL")}
              </span>
            </div>
            
            {!isInitializing && (
              <div className="mt-4 text-center">
                 <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Overall Score</div>
                 <div className="text-2xl font-bold text-white">{telemetry.overall_score}%</div>
              </div>
            )}
          </div>

          {/* Telemetry Metrics List */}
          <div className="flex-1 min-h-0 bg-slate-900/40 rounded-2xl border border-white/10 backdrop-blur-sm p-5 flex flex-col relative">
            <h3 className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-4 pb-2 border-b border-white/5">Diagnostic Breakdown</h3>
            
            <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-3">
              {Object.keys(telemetry.metrics).length === 0 ? (
                <div className="text-slate-600 text-xs italic text-center mt-10 font-mono uppercase tracking-widest">Waiting for target data...</div>
              ) : (
                Object.entries(telemetry.metrics).map(([label, value]) => (
                  <TelemetryGaugeCard key={label} label={label} value={value} />
                ))
              )}
            </div>
          </div>

        </div>
      </main>

      {/* Floating Voice Command Bar */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex flex-col items-center">
        {telemetry.last_command && (
           <div className="mb-3 px-4 py-1.5 bg-black/60 backdrop-blur-md rounded-full border border-white/10 text-xs font-mono text-slate-300">
             Heard: <span className="text-blue-400 font-bold uppercase">"{telemetry.last_command}"</span>
           </div>
        )}
        <div className="flex items-center p-2 bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-full shadow-[0_10px_40px_rgba(0,0,0,0.5)]">
          <button 
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onMouseLeave={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
            className={`flex items-center space-x-3 px-8 py-4 rounded-full font-bold uppercase tracking-widest text-sm transition-all relative overflow-hidden
              ${isRecording 
                ? 'bg-blue-600 text-white shadow-[0_0_30px_rgba(37,99,235,0.5)] scale-105' 
                : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'}`}
          >
            {isRecording && <div className="absolute inset-0 bg-blue-400/20 animate-ping rounded-full"></div>}
            <Mic className={`w-5 h-5 relative z-10 ${isRecording ? 'text-white animate-pulse' : 'text-blue-500'}`} />
            <span className="relative z-10">{isRecording ? "Listening..." : "Hold to Speak"}</span>
          </button>
        </div>
      </div>

    </motion.div>
  );
}

function TelemetryGaugeCard({ label, value }: { label: string; value: any }) {
  if (typeof value === "number") return null; 
  const isPass = value.status === "pass";
  return (
    <div className={`p-3 rounded-lg border bg-black/20 backdrop-blur-sm transition-colors
      ${isPass ? 'border-emerald-500/20 hover:border-emerald-500/40' : 'border-red-500/20 hover:border-red-500/40'}`}>
      <div className="flex justify-between items-center mb-1.5">
        <h4 className="text-[11px] font-bold text-slate-300 tracking-wider uppercase">{label}</h4>
        <div className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-widest ${isPass ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
          {isPass ? 'PASS' : 'FAIL'}
        </div>
      </div>
      <div className="text-[11px] text-slate-500 font-mono leading-relaxed">
        {value.reason}
      </div>
    </div>
  );
}
"""

start_idx = content.find("function Dashboard({")
end_idx = content.find("// RESULTS SCREEN")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + dashboard_new + "\n\n// ==========================================\n" + content[end_idx:]
    with open("/Users/shankumar/drill/web-ui/src/app/page.tsx", "w") as f:
        f.write(content)
else:
    print("Could not find insertion markers.")
