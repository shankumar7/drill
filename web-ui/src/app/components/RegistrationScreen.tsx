"use client";
import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { ChevronRightCircle, Camera, Check, Download, RefreshCw, Trash2 } from "lucide-react";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

export function RegistrationScreen({ onComplete }: { onComplete: (cadet: any) => void }) {
  const BASE_URL = "http://localhost:8000";
  const [mode, setMode] = useState<"choose" | "register" | "login">("choose");
  const [name, setName] = useState("");
  const [pin, setPin] = useState("");
  const [image, setImage] = useState<string | null>(null);
  const [cadetUnit, setCadetUnit] = useState("");
  const [cadetInstructor, setCadetInstructor] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [cadets, setCadets] = useState<any[]>([]);
  const [frontCamId, setFrontCamId] = useState<number>(0);
  const pinInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (mode === "login" && pinInputRef.current) {
      const timer = setTimeout(() => {
        pinInputRef.current?.focus();
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [mode]);

  useEffect(() => {
    fetch("http://localhost:8000/api/cadets")
      .then(res => res.json())
      .then(data => { if (data.status === "ok") setCadets(data.cadets); })
      .catch(err => console.error(err));

    fetch("http://localhost:8000/api/settings")
      .then(res => res.json())
      .then(data => {
        if (data && data.camera_mapping && data.camera_mapping.front !== undefined) {
          setFrontCamId(data.camera_mapping.front);
        }
      })
      .catch(err => console.error(err));
  }, []);

  const capturePhoto = async () => {
    try {
      const res = await fetch(`${BASE_URL}/api/snapshot/${frontCamId}`);
      const data = await res.json();
      if (data.status === "ok") {
        setImage(data.image);
      } else {
        setError(data.message || "Failed to capture photo");
      }
    } catch (err) {
      console.error("Capture error:", err);
      setError("Webcam capture error");
    }
  };

  const handleRegister = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
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
        body: JSON.stringify({ name, pin, image, unit: cadetUnit, instructor: cadetInstructor })
      });
      const data = await res.json();
      if (data.status === "ok") {
        onComplete({ id: data.cadet_id, name: data.name, unit: cadetUnit, instructor: cadetInstructor });
      } else {
        setError(data.message || "Registration failed");
      }
    } catch (e) {
      setError("Network error");
    }
    setLoading(false);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pin.length !== 4) return;
    try {
      const res = await fetch(`${BASE_URL}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pin })
      });
      const data = await res.json();
      if (data.status === "ok") {
        onComplete(data.user);
      } else {
        setError("Invalid PIN");
      }
    } catch (e) {
      setError("Network error");
    }
  };

  const downloadReport = async (cadet: any, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const res = await fetch(`${BASE_URL}/api/cadets/${cadet.id}/sessions`);
      const data = await res.json();
      
      // Fetch settings for dynamic instructor name & unit name
      const settingsRes = await fetch(`${BASE_URL}/api/settings`).catch(() => null);
      const settingsData = settingsRes ? await settingsRes.json().catch(() => ({})) : {};
      const instructor = cadet.instructor || settingsData.instructor_name || "Lt Col K Srinath";
      const unit = cadet.unit || settingsData.unit_name || "Simulation Development Division (SDD), MCEME";

      if (data.status === "ok") {
        const doc = new jsPDF();
        
        // 1. Load SDD Logo Image as base64
        const logoUrl = "/top_right_logo.png";
        let logoBase64: string | null = null;
        try {
          logoBase64 = await new Promise<string>((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = "Anonymous";
            img.onload = () => {
              const canvas = document.createElement("canvas");
              canvas.width = img.width;
              canvas.height = img.height;
              const ctx = canvas.getContext("2d");
              if (ctx) {
                ctx.drawImage(img, 0, 0);
                resolve(canvas.toDataURL("image/png"));
              } else {
                reject();
              }
            };
            img.onerror = () => reject();
            img.src = logoUrl;
          });
        } catch (err) {
          console.warn("Could not load SDD logo image", err);
        }

        // Draw Logo if loaded
        if (logoBase64) {
          doc.addImage(logoBase64, "PNG", 15, 11, 16, 16);
        }

        // 2. Header Text
        doc.setFont("helvetica", "bold");
        doc.setFontSize(11);
        doc.setTextColor(30, 41, 59); // Slate-800
        doc.text("SIMULATION DEVELOPMENT DIVISION (SDD), MCEME", logoBase64 ? 35 : 15, 16);
        
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8.5);
        doc.setTextColor(100, 116, 139); // Slate-500
        doc.text("MILITARY DRILL ANALYSIS & EVALUATION SYSTEM", logoBase64 ? 35 : 15, 21);
        
        doc.setFont("helvetica", "bold");
        doc.setFontSize(13);
        doc.setTextColor(15, 23, 42); // Slate-900
        doc.text("CADET DRILL EVALUATION REPORT", logoBase64 ? 35 : 15, 27);

        // Divider Line
        doc.setDrawColor(203, 213, 225); // Slate-300
        doc.setLineWidth(0.5);
        doc.line(15, 30, 195, 30);

        // 3. Cadet Profile Info Block
        doc.setFillColor(248, 250, 252); // Slate-50
        doc.setDrawColor(226, 232, 240); // Slate-200
        doc.rect(15, 34, 180, 27, "FD");

        // Cadet Info
        doc.setFont("helvetica", "bold");
        doc.setFontSize(9);
        doc.setTextColor(15, 23, 42);
        doc.text(`CADET ID / ID:  #${cadet.id}`, 20, 40);
        doc.text(`CADET NAME:     ${cadet.name.toUpperCase()}`, 20, 46);
        
        doc.setFont("helvetica", "normal");
        doc.setTextColor(71, 85, 105);
        const truncateUnit = unit.length > 55 ? unit.substring(0, 52) + "..." : unit;
        doc.text(`UNIT / BATCH:   ${truncateUnit.toUpperCase()}`, 20, 52);
        doc.text(`GENERATED:      ${new Date().toLocaleString()}`, 20, 57);

        // Score Stats (Right Side of Profile Box)
        const overallScore = cadet.avg_score != null ? Math.round(cadet.avg_score) : 0;
        const accuracy = cadet.accuracy != null ? Math.round(cadet.accuracy) : 0;

        doc.setFont("helvetica", "bold");
        doc.setTextColor(71, 85, 105);
        doc.text("AVERAGE SCORE:", 132, 40);
        doc.setFontSize(12);
        doc.setTextColor(30, 58, 138); // Deep Navy Blue
        doc.text(`${overallScore}%`, 166, 40);

        doc.setFont("helvetica", "bold");
        doc.setFontSize(9);
        doc.setTextColor(71, 85, 105);
        doc.text("CONSISTENCY:", 132, 46);
        doc.setFontSize(12);
        doc.setTextColor(30, 58, 138);
        doc.text(`${accuracy}%`, 166, 46);

        // Calculate Status
        let statusStr = "FAIL";
        let statusColor = [185, 28, 28]; // Red
        if (overallScore >= 85) {
          statusStr = "PASS (EXCELLENT)";
          statusColor = [21, 128, 61]; // Green
        } else if (overallScore >= 75) {
          statusStr = "PASS (SATISFACTORY)";
          statusColor = [30, 58, 138]; // Blue
        }

        doc.setFont("helvetica", "bold");
        doc.setFontSize(9);
        doc.setTextColor(71, 85, 105);
        doc.text("STATUS:", 132, 52);
        doc.setTextColor(statusColor[0], statusColor[1], statusColor[2]);
        doc.text(statusStr, 166, 52);

        // 4. Detailed Session History Table
        const tableData = data.sessions.map((s: any) => [
          new Date(s.timestamp).toLocaleString(),
          s.drill_type.replace(/_/g, " ").toUpperCase(),
          `${Math.round(s.score)}%`,
          s.is_pass ? "PASS" : "FAIL",
          s.cycle_count
        ]);

        autoTable(doc, {
          startY: 65,
          head: [["Date & Time", "Drill Type", "Score", "Result", "Cycles"]],
          body: tableData,
          theme: "grid",
          headStyles: {
            fillColor: [30, 41, 59], // Slate-700
            textColor: [255, 255, 255],
            fontSize: 9,
            fontStyle: "bold",
            halign: "center",
          },
          columnStyles: {
            0: { cellWidth: 50, halign: "left" },
            1: { cellWidth: 60, halign: "left" },
            2: { cellWidth: 20, halign: "center" },
            3: { cellWidth: 30, halign: "center" },
            4: { cellWidth: 20, halign: "center" }
          },
          styles: {
            fontSize: 8.5,
            cellPadding: 3,
            valign: "middle"
          },
          alternateRowStyles: {
            fillColor: [248, 250, 252], // Slate-50
          },
          didParseCell: (cellData) => {
            if (cellData.column.index === 3) {
              if (cellData.cell.text[0] === "PASS") {
                cellData.cell.styles.textColor = [21, 128, 61]; // green
                cellData.cell.styles.fontStyle = "bold";
              } else if (cellData.cell.text[0] === "FAIL") {
                cellData.cell.styles.textColor = [185, 28, 28]; // red
                cellData.cell.styles.fontStyle = "bold";
              }
            }
          }
        });

        // 5. Assessment & Remarks Section
        const finalY = (doc as any).lastAutoTable.finalY || 150;
        
        // Draw light line divider
        doc.setDrawColor(226, 232, 240);
        doc.setLineWidth(0.5);
        doc.line(15, finalY + 8, 195, finalY + 8);

        doc.setFont("helvetica", "bold");
        doc.setFontSize(10);
        doc.setTextColor(15, 23, 42);
        doc.text("PERFORMANCE ASSESSMENT & REMARKS", 15, finalY + 15);

        // Choose remark text based on score
        let remarkText = "";
        if (overallScore >= 85) {
          remarkText = "The cadet demonstrates superior postural stability, precise foot spacing, and robust arm lock alignments. Standard of performance meets the official military guidelines for excellence.";
        } else if (overallScore >= 75) {
          remarkText = "Satisfactory execution of drill moves. Minor deviations observed in arm separation or heel alignments. Passing performance, but continuous practice is advised for perfection.";
        } else {
          remarkText = "Significant alignment deviations or instability detected. Cadet needs additional supervisor guidance, focusing on heel contact, arm pinning, and step locking rules.";
        }

        doc.setFont("helvetica", "normal");
        doc.setFontSize(9);
        doc.setTextColor(71, 85, 105);
        const splitRemarks = doc.splitTextToSize(remarkText, 180);
        doc.text(splitRemarks, 15, finalY + 21);

        // 6. Signature Section
        const sigY = finalY + 21 + (splitRemarks.length * 5) + 15;
        
        doc.setFont("helvetica", "bold");
        doc.setFontSize(9.5);
        doc.setTextColor(15, 23, 42);
        doc.text("INSTRUCTOR EVALUATION SIGN-OFF", 15, sigY);

        doc.setDrawColor(148, 163, 184); // Slate-400
        doc.setLineWidth(0.5);
        doc.line(15, sigY + 8, 80, sigY + 8); // Line for signature

        doc.setFont("helvetica", "normal");
        doc.setFontSize(8.5);
        doc.setTextColor(100, 116, 139);
        doc.text(`NAME:  ${instructor.toUpperCase()}`, 15, sigY + 13);
        doc.text("TITLE: SUPERVISING OFFICER / DRILL INSTRUCTOR", 15, sigY + 18);
        doc.text(`UNIT:  ${unit.toUpperCase()}`, 15, sigY + 23);

        // 7. Footer
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.setTextColor(148, 163, 184);
        doc.text("Simulation Development Division (SDD), MCEME — Automated AI System", 105, 287, { align: "center" });
        doc.text("Page 1 of 1", 195, 287, { align: "right" });

        // Save PDF
        doc.save(`${cadet.name}_Drill_Report.pdf`);
      }
    } catch (e) {
      console.error("Failed to download PDF", e);
    }
  };

  const handleDelete = async (cadetId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this cadet and all their sessions?")) {
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/api/cadets/${cadetId}`, {
        method: "DELETE"
      });
      const data = await res.json();
      if (data.status === "ok") {
        setCadets(prev => prev.filter(c => c.id !== cadetId));
      } else {
        alert(data.message || "Failed to delete cadet");
      }
    } catch (err) {
      console.error("Delete error:", err);
      alert("Failed to delete cadet");
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-stone-950">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-900/20 via-stone-950 to-stone-950"></div>
        <div className="absolute inset-0 opacity-20 mix-blend-overlay" style={{ backgroundImage: "url('data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E')" }}></div>
      </div>

      <div className={`relative z-10 bg-stone-900/40 backdrop-blur-3xl border border-white/10 p-8 sm:p-12 flex flex-col transition-all shadow-[0_0_100px_rgba(0,0,0,0.5)] ${mode === "choose" ? "w-[95vw] h-[95vh] rounded-[40px]" : "max-w-lg rounded-3xl w-full items-center"}`}>
        
        {mode !== "choose" && (
          <h2 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-stone-100 to-stone-500 uppercase tracking-widest mb-8 text-center drop-shadow-sm">
            {mode === "register" ? "New Cadet" : "Cadet Login"}
          </h2>
        )}
        
        {error && <div className="bg-red-950/80 text-red-400 p-4 rounded-xl mb-6 w-full text-center text-xs font-black uppercase tracking-widest border border-red-500/20 shadow-lg backdrop-blur-md">{error}</div>}

        {mode === "choose" && (
          <div className="flex flex-col w-full h-full min-h-0">
            <div className="flex flex-col sm:flex-row justify-between items-center mb-10 shrink-0 gap-6">
              <h2 className="text-4xl sm:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-stone-100 to-stone-500 uppercase tracking-widest drop-shadow-sm">
                Cadet Access
              </h2>
              <div className="flex gap-4">
                <button onClick={() => setMode("login")} className="px-8 py-4 bg-stone-800/50 hover:bg-stone-700/80 backdrop-blur-md rounded-full font-bold uppercase tracking-widest transition-all text-[10px] flex items-center gap-2 border border-white/5 text-stone-300 hover:text-white shadow-lg hover:shadow-xl">
                  Manual Login
                </button>
                <button onClick={() => setMode("register")} className="px-8 py-4 bg-emerald-500 hover:bg-emerald-400 rounded-full font-black uppercase tracking-widest transition-all text-[10px] flex items-center gap-2 text-stone-950 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] hover:scale-105">
                  + New Cadet
                </button>
              </div>
            </div>
             
            {cadets.length > 0 ? (
              <div className="flex flex-col gap-4 overflow-y-auto pb-4 flex-1 custom-scrollbar pr-2">
                {cadets.map(c => (
                  <div 
                    key={c.id} 
                    onClick={() => setMode("login")} 
                    className="relative flex flex-col sm:flex-row items-center justify-between bg-stone-900/40 backdrop-blur-xl p-6 rounded-[2rem] border border-white/5 cursor-pointer group hover:bg-stone-800/60 transition-all duration-300 hover:border-emerald-500/50 hover:shadow-[0_10px_30px_rgba(0,0,0,0.3)] overflow-hidden gap-6"
                  >
                    {/* Glow effect on hover */}
                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/0 via-emerald-500/0 to-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                    
                    {/* Profile Section */}
                    <div className="flex items-center gap-6 min-w-[200px]">
                      <div className="relative shrink-0">
                        <div className="absolute inset-0 bg-emerald-500 rounded-full blur-xl opacity-0 group-hover:opacity-30 transition-opacity duration-300" />
                        <img src={c.image_base64} alt={c.name} className="relative w-16 h-16 rounded-full object-cover border-2 border-stone-800 group-hover:border-emerald-500 transition-colors duration-300 shadow-lg" />
                      </div>
                      <div className="flex flex-col items-start">
                        <span className="relative text-stone-200 text-lg font-black uppercase tracking-[0.2em] group-hover:text-emerald-400 transition-colors">{c.name}</span>
                        {c.unit && <span className="text-[9px] text-stone-500 font-bold uppercase tracking-wider mt-0.5 group-hover:text-stone-400 transition-colors">{c.unit}</span>}
                      </div>
                    </div>
                    
                    {/* Metrics Section */}
                    <div className="flex gap-12 items-center flex-1 justify-center sm:justify-start">
                      <div className="flex flex-col items-center sm:items-start min-w-[100px]">
                        <span className="text-[8px] text-stone-500 uppercase font-black tracking-[0.2em] mb-1 leading-tight">Avg Score</span>
                        <span className="text-2xl font-black text-stone-200 group-hover:text-white transition-colors tracking-tighter">
                          {c.avg_score != null ? Math.round(c.avg_score) : 0}
                          <span className="text-sm text-stone-500 ml-0.5">%</span>
                        </span>
                      </div>
                      <div className="flex flex-col items-center sm:items-start min-w-[100px]">
                        <span className="text-[8px] text-stone-500 uppercase font-black tracking-[0.2em] mb-1 leading-tight">Accuracy</span>
                        <span className="text-2xl font-black text-stone-200 group-hover:text-white transition-colors tracking-tighter">
                          {c.accuracy != null ? Math.round(c.accuracy) : 0}
                          <span className="text-sm text-stone-500 ml-0.5">%</span>
                        </span>
                      </div>
                    </div>
                    
                    {/* Actions Section */}
                    <div className="flex items-center gap-4 w-full sm:w-auto justify-end z-10 shrink-0">
                      <button 
                        onClick={(e) => downloadReport(c, e)}
                        className="py-3 px-6 bg-stone-950/80 hover:bg-emerald-500 text-stone-400 hover:text-stone-950 border border-white/5 hover:border-transparent rounded-xl flex items-center justify-center gap-2 text-[10px] font-black uppercase tracking-widest transition-all duration-300 shadow-md hover:scale-105"
                      >
                        <Download className="w-3.5 h-3.5" /> Download Report
                      </button>
                      <button 
                        onClick={(e) => handleDelete(c.id, e)}
                        className="p-3 bg-stone-950/80 hover:bg-red-500 text-stone-500 hover:text-white border border-white/5 hover:border-transparent rounded-xl flex items-center justify-center transition-all duration-300 shadow-md hover:scale-105"
                        title="Delete Cadet"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-32 text-stone-500 bg-stone-900/20 backdrop-blur-md rounded-[2.5rem] border border-white/5 flex-1 shadow-inner">
                <div className="w-24 h-24 rounded-full bg-stone-800/50 flex items-center justify-center mb-8 shadow-inner border border-white/5">
                  <Camera className="w-10 h-10 text-stone-600" />
                </div>
                <p className="uppercase tracking-[0.3em] font-black text-xl text-stone-400 mb-3">No Cadets Registered</p>
                <p className="text-xs font-bold text-stone-600 uppercase tracking-widest">Enlist a new cadet to begin evaluation</p>
              </div>
            )}
          </div>
        )}

        {mode === "login" && (
          <form onSubmit={handleLogin} className="flex flex-col gap-6 w-full max-w-sm mx-auto">
            <div className="text-center mb-4">
              <h3 className="text-stone-200 text-xl font-black uppercase tracking-widest mb-2">Authentication</h3>
              <p className="text-stone-500 text-xs font-bold uppercase tracking-widest">Enter your 4-digit security PIN</p>
            </div>
            <div className="relative">
              <input ref={pinInputRef} autoFocus type="password" placeholder="****" value={pin} onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))} maxLength={4} className="w-full bg-stone-950/50 border border-white/10 rounded-2xl p-6 text-center text-4xl tracking-[1em] text-emerald-400 font-black shadow-inner focus:outline-none focus:border-emerald-500/50 focus:shadow-[0_0_30px_rgba(16,185,129,0.1)] transition-all placeholder:text-stone-800" />
            </div>
            <button type="submit" disabled={loading || pin.length !== 4} className="p-4 bg-stone-800 hover:bg-emerald-900/50 text-stone-300 hover:text-emerald-400 border border-white/5 hover:border-emerald-500/30 rounded-2xl font-black uppercase tracking-widest transition-all disabled:opacity-50 disabled:pointer-events-none mt-2 shadow-lg">
              {loading ? "Authenticating..." : "Login"}
            </button>
            <button type="button" onClick={() => { setMode("choose"); setError(""); setPin(""); }} className="text-stone-500 hover:text-stone-300 text-[10px] font-black uppercase tracking-widest mt-2 hover:underline underline-offset-4">Cancel</button>
          </form>
        )}

        {mode === "register" && (
          <form onSubmit={handleRegister} className="flex flex-col gap-5 w-full max-w-sm mx-auto">

            <input type="text" placeholder="Cadet Name" value={name} onChange={(e) => setName(e.target.value)} className="bg-stone-950/50 border border-white/10 rounded-2xl p-4 text-white text-center font-bold tracking-widest uppercase focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-stone-700 shadow-inner" />
            <input type="text" placeholder="Unit / Batch (Optional)" value={cadetUnit} onChange={(e) => setCadetUnit(e.target.value)} className="bg-stone-950/50 border border-white/10 rounded-2xl p-4 text-white text-center font-bold tracking-widest uppercase focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-stone-700 shadow-inner" />
            <input type="text" placeholder="Instructor Name (Optional)" value={cadetInstructor} onChange={(e) => setCadetInstructor(e.target.value)} className="bg-stone-950/50 border border-white/10 rounded-2xl p-4 text-white text-center font-bold tracking-widest uppercase focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-stone-700 shadow-inner" />
            <input type="password" placeholder="Create 4-digit PIN" value={pin} onChange={(e) => setPin(e.target.value.replace(/\D/g, ''))} maxLength={4} className="bg-stone-950/50 border border-white/10 rounded-2xl p-4 text-center text-2xl tracking-[1em] text-emerald-400 font-black focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-stone-800 shadow-inner" />
            
            <div className="relative bg-stone-950/80 border border-white/10 rounded-2xl h-48 overflow-hidden flex items-center justify-center group shadow-inner">
              {!image ? (
                <>
                  <img src={`${BASE_URL}/api/video_feed/${frontCamId}?raw=true`} className="absolute inset-0 w-full h-full object-cover opacity-40 group-hover:opacity-60 transition-opacity" />
                  <button type="button" onClick={capturePhoto} className="relative z-10 flex flex-col items-center gap-2 p-4 bg-black/40 backdrop-blur-md hover:bg-emerald-900/60 rounded-2xl border border-white/10 hover:border-emerald-500/50 transition-all shadow-lg hover:shadow-emerald-500/20 hover:scale-105">
                    <Camera className="w-8 h-8 text-stone-300 group-hover:text-emerald-400 transition-colors" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-stone-400 group-hover:text-emerald-400">Capture Photo</span>
                  </button>
                  <button type="button" onClick={() => setFrontCamId((frontCamId + 1) % 3)} className="absolute top-3 right-3 z-20 p-2 bg-stone-900/80 backdrop-blur-md rounded-full hover:bg-emerald-600 border border-white/10 transition-colors shadow-lg" title="Switch Camera Source">
                    <RefreshCw className="w-4 h-4 text-white" />
                  </button>
                </>
              ) : (
                <>
                  <img src={image} alt="captured" className="absolute inset-0 w-full h-full object-cover" />
                  <button type="button" onClick={() => setImage(null)} className="relative z-10 px-6 py-3 bg-black/60 backdrop-blur-md rounded-full text-[10px] font-black uppercase tracking-widest text-white border border-white/20 hover:border-red-500 hover:text-red-400 transition-colors shadow-lg">Retake</button>
                </>
              )}
            </div>

            <button type="submit" disabled={loading || pin.length !== 4 || !name || !image} className="p-4 bg-emerald-600/20 hover:bg-emerald-600/40 border border-emerald-500/30 text-emerald-400 rounded-2xl font-black uppercase tracking-widest transition-all mt-2 flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none shadow-lg hover:shadow-emerald-500/20">
              {loading ? "Registering..." : <><Check className="w-5 h-5" /> Complete Enlistment</>}
            </button>
            <button type="button" onClick={() => { setMode("choose"); setError(""); setPin(""); setName(""); setImage(null); setCadetUnit(""); setCadetInstructor(""); }} className="text-stone-500 hover:text-stone-300 text-[10px] font-black uppercase tracking-widest text-center w-full mt-2 hover:underline underline-offset-4">Cancel</button>
          </form>
        )}
      </div>
    </motion.div>
  );
}
