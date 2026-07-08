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
  const videoRef = useRef<HTMLVideoElement>(null);
  
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
      <div className="bg-stone-900 border border-white/10 rounded-3xl p-8 max-w-lg w-full flex flex-col items-center">
        <h2 className="text-3xl font-black text-stone-100 uppercase tracking-widest mb-8">
          {mode === "choose" ? "Cadet Access" : mode === "register" ? "New Cadet" : "Cadet Login"}
        </h2>
        
        {error && <div className="bg-red-900/50 text-red-400 p-3 rounded-lg mb-6 w-full text-center text-sm font-bold">{error}</div>}

        {mode === "choose" && (
          <div className="flex flex-col gap-4 w-full">
            <button onClick={() => setMode("register")} className="p-4 bg-stone-800 hover:bg-stone-700 text-stone-200 rounded-xl font-bold uppercase tracking-wider transition-colors">Register New Cadet</button>
            <button onClick={() => setMode("login")} className="p-4 bg-stone-800 hover:bg-stone-700 text-stone-200 rounded-xl font-bold uppercase tracking-wider transition-colors">Login with PIN</button>
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
