import { Camera, RadioTower } from "lucide-react";
import type { FeedSource } from "@/types/drill";

interface CameraPanelProps {
  feed: FeedSource;
  primary?: boolean;
}

export function CameraPanel({ feed, primary = false }: CameraPanelProps) {
  return (
    <section className={`panel overflow-hidden ${primary ? "min-h-[360px]" : "min-h-[210px]"}`}>
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-100">{feed.label}</h3>
          <p className="text-xs text-slate-500">{feed.perspective}</p>
        </div>
        <span className="inline-flex items-center gap-2 rounded-full border border-slate-600 px-2.5 py-1 text-[11px] font-semibold text-slate-400">
          <RadioTower className="h-3 w-3" />
          {feed.status.toUpperCase()}
        </span>
      </div>

      <div className="relative flex h-full min-h-[inherit] items-center justify-center bg-slate-950">
        <div className="absolute inset-0 camera-grid opacity-70" />
        <div className="absolute left-4 top-4 rounded border border-white/10 bg-black/40 px-2 py-1 text-[11px] font-mono text-slate-400">
          {feed.endpoint}
        </div>
        <div className="relative z-10 flex flex-col items-center text-center">
          <div className="mb-3 rounded-full border border-slate-700 bg-slate-900 p-4">
            <Camera className="h-8 w-8 text-slate-500" />
          </div>
          <p className="text-sm font-semibold text-slate-300">Feed panel ready</p>
          <p className="mt-1 max-w-xs text-xs leading-5 text-slate-500">Connect the Python backend stream here; no CV is running in the frontend.</p>
        </div>
      </div>
    </section>
  );
}
