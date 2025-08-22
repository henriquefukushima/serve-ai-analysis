export interface AnalysisConfig {
  confidence_threshold: number;
  min_serve_duration: number;
  max_serve_duration: number;
  optimize_video: boolean;
  include_landmarks: boolean;
  extract_segments: boolean;
  player_handedness: 'right' | 'left';
}

export interface AnalysisStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  results?: AnalysisResults;
  error?: string;
}

export interface ServeResult {
  serve_id: number;
  start_frame: number;
  end_frame: number;
  duration: number;
  confidence: number;
  video_url: string;
  thumbnail_url?: string;
}

export interface AnalysisResults {
  total_serves: number;
  video_quality: any;
  pose_stats: any;
  serves: ServeResult[];
  config: AnalysisConfig;
}

export interface UploadResponse {
  task_id: string;
  message: string;
  file_size: number;
}
