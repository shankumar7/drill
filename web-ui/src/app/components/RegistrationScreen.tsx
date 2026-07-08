"use client";
import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { ChevronRightCircle, Camera, Check } from "lucide-react";

export function RegistrationScreen({ onComplete }: { onComplete: (cadet: any) => void }) {
  const [mode, setMode] = useState<"choose" | "register" | "login">("choose");
  const [name, setName] = useState("");
  const [pin, setPin] = useState("");
  const [image, setImage] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [cadets, setCadets] = useState<any[]>([]);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  useEffect(() => {
    fetch("http://localhost:8000/api/cadets")
      .then(res => res.json())
      .then(data => { if (data.status === "ok") setCadets(data.cadets); })
      .catch(err => console.error(err));
  }, []);
  useEffect(() => {
    if (mode === "register") {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        })
        .catch(err => console.error("Webcam error:", err));
    } else {
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(t => t.stop());
      }
    }
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(t => t.stop());
      }
    };
  }, [mode]);

  const capturePhoto = () => {
    if (videoRef.current) {
      const canvas = document.createElement("canvas");
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0);
        setImage(canvas.toDataURL("image/jpeg", 0.8));
      }
    }
  };

  const handleRegister = async () => {
    if (!name || pin.length < 4 || !image) {
      setError("Please fill all fields and capture a photo.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, pin, image })
      });
      const data = await res.json();
      if (data.status === "ok") {
        onComplete({ id: data.cadet_id, name: data.name });
      } else {
        setError(data.message || "Registration failed");
      }
    } catch (e) {
      setError("Network error");
    }
    setLoading(false);
  };

  const handleLogin = async () => {
    if (pin.length < 4) {
      setError("Enter valid PIN.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pin })
      });
      const data = await res.json();
      if (data.status === "ok") {
        onComplete(data.user);
      } else {
        setError(data.message || "Login failed");
      }
    } catch (e) {
      setError("Network error");
    }
    setLoading(false);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-stone-950 p-6">
      <div className={`bg-stone-900 border border-white/10 p-8 flex flex-col items-center transition-all ${mode === "choose" ? "max-w-4xl rounded-[40px] w-full" : "max-w-lg rounded-3xl w-full"}`}>
        <h2 className="text-3xl font-black text-stone-100 uppercase tracking-widest mb-8">
          {mode === "choose" ? "Cadet Access" : mode === "register" ? "New Cadet" : "Cadet Login"}
        </h2>
        
        {error && <div className="bg-red-900/50 text-red-400 p-3 rounded-lg mb-6 w-full text-center text-sm font-bold">{error}</div>}

        {mode === "choose" && (
          <div className="flex flex-col w-full h-full">
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-stone-400 text-sm font-bold uppercase tracking-widest">Select Profile</h3>
              <div className="flex gap-4">
                <button onClick={() => setMode("login")} className="px-6 py-3 bg-stone-800 text-stone-300 hover:bg-stone-700 rounded-full font-bold uppercase tracking-wider transition-colors text-xs flex items-center gap-2 border border-white/5">
                  Manual Login
                </button>
                <button onClick={() => setMode("register")} className="px-6 py-3 bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 rounded-full font-bold uppercase tracking-wider transition-colors text-xs flex items-center gap-2 border border-emerald-500/30">
                  + New Cadet
                </button>
              </div>
            </div>
             
            {cadets.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 overflow-y-auto pb-4 max-h-[60vh]">
                {cadets.map(c => (
                  <div key={c.id} onClick={() => setMode("login")} className="flex flex-col items-center bg-stone-950/50 p-6 rounded-2xl border border-white/5 cursor-pointer group hover:bg-stone-900 transition-all hover:border-emerald-500/50 hover:shadow-[0_0_30px_rgba(16,185,129,0.1)]">
                    <img src={c.image_base64} alt={c.name} className="w-24 h-24 rounded-full object-cover border-2 border-white/10 group-hover:border-emerald-500 transition-colors mb-4" />
                    <span className="text-stone-200 text-lg font-black uppercase tracking-widest group-hover:text-emerald-400 mb-4 text-center">{c.name}</span>
                    
                    <div className="flex gap-4 w-full">
                      <div className="flex-1 bg-stone-900/80 rounded-xl p-3 flex flex-col items-center border border-white/5">
                        <span className="text-[10px] text-stone-500 uppercase font-black tracking-widest mb-1 text-center leading-tight">Avg Score</span>
                        <span className="text-lg font-black text-stone-300">{c.avg_score != null ? Math.round(c.avg_score) : 0}%</span>
                      </div>
                      <div className="flex-1 bg-stone-900/80 rounded-xl p-3 flex flex-col items-center border border-white/5">
                        <span className="text-[10px] text-stone-500 uppercase font-black tracking-widest mb-1 text-center leading-tight">Accuracy</span>
                        <span className="text-lg font-black text-stone-300">{c.accuracy != null ? Math.round(c.accuracy) : 0}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-20 text-stone-500 bg-stone-950/30 rounded-3xl border border-white/5">
                <Camera className="w-16 h-16 mb-6 opacity-20" />
                <p className="uppercase tracking-widest font-black text-sm text-stone-600">No Cadets Registered</p>
                <p className="text-xs mt-2 opacity-50">Register a new cadet to begin evaluation</p>
              </div>
            )}
          </div>
        )}

        {mode === "login" && (
          <div className="flex flex-col gap-6 w-full">
            <input type="password" placeholder="Enter 4-digit PIN" value={pin} onChange={(e) => setPin(e.target.value)} maxLength={4} className="bg-stone-950 border border-white/10 rounded-xl p-4 text-center text-2xl tracking-[1em] text-white focus:outline-none focus:border-stone-500" />
            <button onClick={handleLogin} disabled={loading} className="p-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold uppercase tracking-wider transition-colors">{loading ? "..." : "Login"}</button>
            <button onClick={() => setMode("choose")} className="text-stone-500 hover:text-stone-300 text-sm font-bold uppercase tracking-widest mt-4">Back</button>
          </div>
        )}

        {mode === "register" && (
          <div className="flex flex-col gap-5 w-full">
            <input type="text" placeholder="Cadet Name" value={name} onChange={(e) => setName(e.target.value)} className="bg-stone-950 border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-stone-500" />
            <input type="password" placeholder="Create 4-digit PIN" value={pin} onChange={(e) => setPin(e.target.value)} maxLength={4} className="bg-stone-950 border border-white/10 rounded-xl p-4 text-center text-2xl tracking-[1em] text-white focus:outline-none focus:border-stone-500" />
            
            <div className="relative bg-stone-950 border border-white/10 rounded-xl h-48 overflow-hidden flex items-center justify-center">
              {!image ? (
                <>
                  <video ref={videoRef} autoPlay playsInline muted className="absolute inset-0 w-full h-full object-cover opacity-50" />
                  <button onClick={capturePhoto} className="relative z-10 p-3 bg-white/20 backdrop-blur-md hover:bg-white/30 rounded-full transition-colors">
                    <Camera className="w-6 h-6 text-white" />
                  </button>
                </>
              ) : (
                <>
                  <img src={image} alt="captured" className="absolute inset-0 w-full h-full object-cover" />
                  <button onClick={() => setImage(null)} className="relative z-10 px-4 py-2 bg-stone-900/80 backdrop-blur-md rounded-full text-xs font-bold uppercase tracking-widest text-white border border-white/20 hover:bg-stone-800 transition-colors">Retake</button>
                </>
              )}
            </div>

            <button onClick={handleRegister} disabled={loading} className="p-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold uppercase tracking-wider transition-colors mt-2 flex items-center justify-center gap-2">
              {loading ? "..." : <><Check className="w-5 h-5" /> Register & Begin</>}
            </button>
            <button onClick={() => setMode("choose")} className="text-stone-500 hover:text-stone-300 text-sm font-bold uppercase tracking-widest mt-2 text-center w-full">Back</button>
          </div>
        )}
      </div>
    </motion.div>
  );
}
