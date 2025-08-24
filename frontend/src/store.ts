import { create } from 'zustand';
import { AnalysisConfig, AnalysisStatus, AnalysisResults } from './types';

interface AppState {
  // Current analysis
  currentTaskId: string | null;
  analysisStatus: AnalysisStatus | null;
  analysisResults: AnalysisResults | null;
  
  // Configuration
  config: AnalysisConfig;
  
  // UI state
  isUploading: boolean;
  isProcessing: boolean;
  error: string | null;
  
  // Actions
  setCurrentTask: (taskId: string) => void;
  setAnalysisStatus: (status: AnalysisStatus) => void;
  setAnalysisResults: (results: AnalysisResults) => void;
  setConfig: (config: Partial<AnalysisConfig>) => void;
  setUploading: (uploading: boolean) => void;
  setProcessing: (processing: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const defaultConfig: AnalysisConfig = {
  confidence_threshold: 0.7,
  min_serve_duration: 1.5,
  max_serve_duration: 8.0,
  optimize_video: true,
  include_landmarks: true,
  extract_segments: true,
  player_handedness: 'right',
  // New parameters
  video_quality: 'medium',
  landmark_style: 'skeleton',
  output_format: 'mp4',
  include_metadata: true,
  serve_numbering: 'sequential',
  compression_level: 5,
};

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  currentTaskId: null,
  analysisStatus: null,
  analysisResults: null,
  config: defaultConfig,
  isUploading: false,
  isProcessing: false,
  error: null,
  
  // Actions
  setCurrentTask: (taskId) => set({ currentTaskId: taskId }),
  setAnalysisStatus: (status) => set({ analysisStatus: status }),
  setAnalysisResults: (results) => set({ analysisResults: results }),
  setConfig: (newConfig) => set((state) => ({ 
    config: { ...state.config, ...newConfig } 
  })),
  setUploading: (uploading) => set({ isUploading: uploading }),
  setProcessing: (processing) => set({ isProcessing: processing }),
  setError: (error) => set({ error }),
  reset: () => set({
    currentTaskId: null,
    analysisStatus: null,
    analysisResults: null,
    isUploading: false,
    isProcessing: false,
    error: null,
  }),
}));
