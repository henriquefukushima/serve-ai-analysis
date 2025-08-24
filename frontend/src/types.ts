export interface AnalysisConfig {
  confidence_threshold: number;
  min_serve_duration: number;
  max_serve_duration: number;
  optimize_video: boolean;
  include_landmarks: boolean;
  extract_segments: boolean;
  player_handedness: 'right' | 'left';
  // New parameters
  video_quality: 'low' | 'medium' | 'high' | 'original';
  landmark_style: 'points' | 'skeleton' | 'both';
  output_format: 'mp4' | 'avi' | 'mov';
  include_metadata: boolean;
  serve_numbering: 'sequential' | 'timestamp';
  compression_level: number; // 1-10
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
  task_id: string;
  total_serves: number;
  serve_segments: ServeSegment[];
  video_quality: any;
  download_url: string;
  config_used: AnalysisConfig;
  zip_path: string;
}

export interface ServeSegment {
  serve_id: number;
  start_frame: number;
  end_frame: number;
  duration: number;
  confidence: number;
  video_path: string;
  has_landmarks: boolean;
  ball_toss_frame: number;
  contact_frame: number;
  follow_through_frame: number;
}

export interface UploadResponse {
  task_id: string;
  message: string;
  file_size: number;
}
