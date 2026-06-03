"use client";

import React from "react";
import { motion } from "framer-motion";

interface GaugeProps {
  label: string;
  value: number; // 0 to 100
  color?: string;
}

export function Gauge({ label, value, color = "#3B82F6" }: GaugeProps) {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  let displayColor = color;
  if (value < 50) displayColor = "#EF4444"; // Red
  else if (value < 80) displayColor = "#F59E0B"; // Yellow
  else displayColor = "#10B981"; // Green

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative w-32 h-32 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            className="text-slate-800"
          />
          <motion.circle
            cx="64"
            cy="64"
            r={radius}
            stroke={displayColor}
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1, ease: "easeOut" }}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold text-white tracking-tighter">
            {Math.round(value)}
          </span>
          <span className="text-xs text-slate-400 mt-1">%</span>
        </div>
      </div>
      <h3 className="mt-4 text-sm font-medium text-slate-300 uppercase tracking-wider text-center">
        {label}
      </h3>
    </div>
  );
}
