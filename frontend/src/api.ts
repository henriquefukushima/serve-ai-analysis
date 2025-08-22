import { AnalysisConfig, AnalysisStatus, AnalysisResults, UploadResponse } from './types';

const API_BASE = '/api';

export const api = {
  async uploadVideo(file: File, config: AnalysisConfig): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('config', JSON.stringify(config));
    
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }
    
    return response.json();
  },

  async getAnalysisStatus(taskId: string): Promise<AnalysisStatus> {
    const response = await fetch(`${API_BASE}/status/${taskId}`);
    
    if (!response.ok) {
      throw new Error(`Status check failed: ${response.statusText}`);
    }
    
    return response.json();
  },

  async getAnalysisResults(taskId: string): Promise<AnalysisResults> {
    const response = await fetch(`${API_BASE}/results/${taskId}`);
    
    if (!response.ok) {
      throw new Error(`Results fetch failed: ${response.statusText}`);
    }
    
    return response.json();
  },

  getServeVideoUrl(taskId: string, serveId: number): string {
    return `${API_BASE}/static/${taskId}_serve_${serveId}.mp4`;
  },

  async downloadServeVideo(taskId: string, serveId: number): Promise<Blob> {
    const response = await fetch(`${API_BASE}/download/${taskId}/${serveId}`);
    
    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }
    
    return response.blob();
  },

  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${API_BASE}/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    
    return response.json();
  },
};
