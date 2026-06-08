import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { getFromStorage, saveToStorage } from '@/utils/storage';

interface EvaluationRecord {
  id: string;
  cadetId: string;
  drill: string;
  timestamp: number;
  result: 'PASS' | 'FAIL';
  details?: string[];
}

interface EvaluationContextProps {
  cadetId: string;
  setCadetId: (id: string) => void;
  selectedDrill: string;
  setSelectedDrill: (drill: string) => void;
  startEvaluation: () => Promise<void>;
  evaluationResult: 'PASS' | 'FAIL' | null;
  setEvaluationResult: (res: 'PASS' | 'FAIL' | null) => void;
  log: EvaluationRecord[];
  addRecord: (record: EvaluationRecord) => void;
}

const EvaluationContext = createContext<EvaluationContextProps | undefined>(undefined);

export const EvaluationProvider = ({ children }: { children: ReactNode }) => {
  const [cadetId, setCadetId] = useState('');
  const [selectedDrill, setSelectedDrill] = useState('Savadhan');
  const [evaluationResult, setEvaluationResult] = useState<'PASS' | 'FAIL' | null>(null);
  const [log, setLog] = useState<EvaluationRecord[]>([]);

  // Load log from localStorage on mount
  useEffect(() => {
    const stored = getFromStorage('evaluationLog');
    if (stored) setLog(stored);
  }, []);

  // Persist log when it changes
  useEffect(() => {
    saveToStorage('evaluationLog', log);
  }, [log]);

  const addRecord = (record: EvaluationRecord) => {
    setLog((prev) => [record, ...prev]);
  };

  const startEvaluation = async () => {
    // Placeholder – actual evaluation triggered from UI components
    // This function can be expanded later if needed.
    return;
  };

  return (
    <EvaluationContext.Provider
      value={{
        cadetId,
        setCadetId,
        selectedDrill,
        setSelectedDrill,
        startEvaluation,
        evaluationResult,
        setEvaluationResult,
        log,
        addRecord,
      }}
    >
      {children}
    </EvaluationContext.Provider>
  );
};

export const useEvaluation = () => {
  const context = useContext(EvaluationContext);
  if (!context) {
    throw new Error('useEvaluation must be used within EvaluationProvider');
  }
  return context;
};
