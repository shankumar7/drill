"use client";

import React, { useState, useRef, useEffect } from 'react';
import { useEvaluation } from '@/context/EvaluationContext';
import CameraFeed, { CameraFeedHandle } from '@/components/CameraFeed';
import PostureAnalyzer from '@/components/PostureAnalyzer';
import RuleExtractor, { Rule } from '@/components/RuleExtractor';
import { v4 as uuidv4 } from 'uuid';

export default function EvaluationPage() {
  const {
    cadetId,
    setCadetId,
    selectedDrill,
    setSelectedDrill,
    evaluationResult,
    setEvaluationResult,
    log,
    addRecord,
  } = useEvaluation();

  const [availableDevices, setAvailableDevices] = useState<MediaDeviceInfo[]>([]);
  const [loadingDevices, setLoadingDevices] = useState(true);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [rules, setRules] = useState<Rule[]>([]);

  const camRef1 = useRef<CameraFeedHandle>(null);
  const camRef2 = useRef<CameraFeedHandle>(null);

  // Load camera devices on mount
  useEffect(() => {
    navigator.mediaDevices
      .enumerateDevices()
      .then((devices) => {
        const videoDevices = devices.filter((d) => d.kind === 'videoinput');
        setAvailableDevices(videoDevices);
      })
      .catch(console.error)
      .finally(() => setLoadingDevices(false));
  }, []);

  // Load rules from PDF on mount using RuleExtractor
  useEffect(() => {
    const extractor = new RuleExtractor('/drill_rules.pdf');
    extractor.extract().then(setRules).catch(console.error);
  }, []);

  const startEvaluation = async () => {
    if (!camRef1.current || !camRef2.current) return;
    setIsEvaluating(true);
    setEvaluationResult(null);
    // Capture 5 seconds at 30 fps
    const duration = 5000;
    const fps = 30;
    const [frames1, frames2] = await Promise.all([
      camRef1.current.captureFrames(duration, fps),
      camRef2.current.captureFrames(duration, fps),
    ]);
    // Merge frames (simple concatenation)
    const allFrames = frames1.concat(frames2);
    const analyzer = new PostureAnalyzer(rules);
    const { pass, details } = await analyzer.analyze(allFrames);
    setEvaluationResult(pass ? 'PASS' : 'FAIL');
    const record = {
      id: uuidv4(),
      cadetId,
      drill: selectedDrill,
      timestamp: Date.now(),
      result: pass ? 'PASS' : 'FAIL',
      details,
    };
    addRecord(record);
    setIsEvaluating(false);
  };

  return (
    <div className="p-8 min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white">
      <h1 className="text-4xl font-bold mb-6 text-center">Drill Evaluation</h1>
      <div className="max-w-3xl mx-auto bg-gray-900 bg-opacity-60 rounded-xl glass-card p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <label className="block">
            <span className="text-sm font-medium">Cadet ID</span>
            <input
              type="text"
              value={cadetId}
              onChange={(e) => setCadetId(e.target.value)}
              className="mt-1 block w-full rounded bg-gray-800 border-gray-700 focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50"
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium">Drill</span>
            <select
              value={selectedDrill}
              onChange={(e) => setSelectedDrill(e.target.value)}
              className="mt-1 block w-full rounded bg-gray-800 border-gray-700 focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50"
            >
              <option value="Savadhan">Savadhan</option>
              {/* Future drills can be added here */}
            </select>
          </label>
        </div>
        <div className="flex justify-center space-x-4 mb-4">
          <button
            onClick={startEvaluation}
            disabled={isEvaluating || !cadetId || loadingDevices || availableDevices.length < 2}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 rounded transition transform hover:scale-105"
          >
            {isEvaluating ? 'Evaluating…' : 'Start Evaluation'}
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {availableDevices.slice(0, 2).map((device) => (
            <CameraFeed
              key={device.deviceId}
              deviceId={device.deviceId}
              cadetId={cadetId}
              ref={device.label.includes('front') ? camRef1 : camRef2}
              className="rounded shadow-lg"
            />
          ))}
        </div>
        {evaluationResult && (
          <div
            className={`mt-4 text-2xl font-bold text-center p-4 rounded ${
              evaluationResult === 'PASS' ? 'bg-green-600' : 'bg-red-600'
            } animate-pulse`}
          >
            {evaluationResult}
          </div>
        )}
        <hr className="my-6 border-gray-600" />
        <h2 className="text-xl font-semibold mb-2">Past Evaluations</h2>
        <table className="w-full table-auto text-sm">
          <thead>
            <tr className="bg-gray-800">
              <th className="px-2 py-1">Time</th>
              <th className="px-2 py-1">Cadet</th>
              <th className="px-2 py-1">Drill</th>
              <th className="px-2 py-1">Result</th>
            </tr>
          </thead>
          <tbody>
            {log.map((r) => (
              <tr key={r.id} className="border-b border-gray-700">
                <td className="px-2 py-1">{new Date(r.timestamp).toLocaleTimeString()}</td>
                <td className="px-2 py-1">{r.cadetId}</td>
                <td className="px-2 py-1">{r.drill}</td>
                <td className="px-2 py-1 font-bold text-{r.result === 'PASS' ? 'green-400' : 'red-400'}">
                  {r.result}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
