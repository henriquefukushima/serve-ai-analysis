import React from 'react';
import { Download, FileArchive, FileVideo, BarChart3 } from 'lucide-react';
import { useAppStore } from '../store';

export const ResultsDownload: React.FC = () => {
  const { analysisResults, currentTaskId } = useAppStore();

  if (!analysisResults || !currentTaskId) return null;

  const handleDownload = async () => {
    try {
      const response = await fetch(`/api/download/${currentTaskId}/archive`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `serve_analysis_${currentTaskId}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        throw new Error(`Download failed: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    }
  };

  const totalServes = analysisResults.total_serves || 0;
  const avgConfidence = analysisResults.serve_segments && analysisResults.serve_segments.length > 0
    ? analysisResults.serve_segments.reduce((sum: number, seg) => sum + seg.confidence, 0) / analysisResults.serve_segments.length
    : 0;

  return (
    <div className="card">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Analysis Complete!</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="flex items-center justify-center p-4 bg-blue-50 rounded-lg">
            <FileVideo className="w-8 h-8 text-blue-500 mr-3" />
            <div className="text-left">
              <p className="text-lg font-semibold">{totalServes}</p>
              <p className="text-sm text-gray-600">Serves Detected</p>
            </div>
          </div>
          
          <div className="flex items-center justify-center p-4 bg-green-50 rounded-lg">
            <BarChart3 className="w-8 h-8 text-green-500 mr-3" />
            <div className="text-left">
              <p className="text-lg font-semibold">{(avgConfidence * 100).toFixed(1)}%</p>
              <p className="text-sm text-gray-600">Avg Confidence</p>
            </div>
          </div>
          
          <div className="flex items-center justify-center p-4 bg-purple-50 rounded-lg">
            <FileArchive className="w-8 h-8 text-purple-500 mr-3" />
            <div className="text-left">
              <p className="text-lg font-semibold">Ready</p>
              <p className="text-sm text-gray-600">For Download</p>
            </div>
          </div>
        </div>
        
        <button
          onClick={handleDownload}
          className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Download className="w-5 h-5 mr-2" />
          Download Serve Analysis
        </button>
        
        <p className="text-sm text-gray-500 mt-4">
          ZIP file contains individual serve videos, analysis report, and configuration summary
        </p>
        
        <div className="mt-6 p-4 bg-gray-50 rounded-lg text-left">
          <h3 className="font-medium text-gray-900 mb-2">Archive Contents:</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• <strong>serves/</strong> - Individual serve video clips</li>
            <li>• <strong>analysis_report.html</strong> - Detailed HTML report</li>
            <li>• <strong>config_summary.json</strong> - Analysis configuration</li>
            <li>• <strong>README.md</strong> - Usage instructions</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
