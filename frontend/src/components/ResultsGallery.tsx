import React, { useState } from 'react';
import { Download, Play, Eye, Clock, Target } from 'lucide-react';
import { useAppStore } from '../store';
import { ServeResult } from '../types';
import { api } from '../api';

interface ResultsGalleryProps {
  taskId: string;
}

export const ResultsGallery: React.FC<ResultsGalleryProps> = ({ taskId }) => {
  const { analysisResults } = useAppStore();
  const [selectedServe, setSelectedServe] = useState<ServeResult | null>(null);
  const [isDownloading, setIsDownloading] = useState<number | null>(null);

  if (!analysisResults || analysisResults.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Serves Detected</h3>
          <p className="text-gray-600">
            No tennis serves were detected in the uploaded video. Try adjusting the analysis parameters or upload a different video.
          </p>
        </div>
      </div>
    );
  }

  const handleDownload = async (serve: ServeResult) => {
    try {
      setIsDownloading(serve.serve_id);
      const blob = await api.downloadServeVideo(taskId, serve.serve_id);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `serve_${serve.serve_id}.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setIsDownloading(null);
    }
  };

  const formatDuration = (duration: number) => {
    const seconds = Math.round(duration / 30); // Assuming 30 fps
    return `${seconds}s`;
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
            <p className="text-gray-600 mt-1">
              Found {analysisResults.length} serve{analysisResults.length !== 1 ? 's' : ''} in your video
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Total Duration</div>
            <div className="text-lg font-semibold text-gray-900">
              {formatDuration(analysisResults.reduce((sum, serve) => sum + serve.duration, 0))}
            </div>
          </div>
        </div>
      </div>

      {/* Serve Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {analysisResults.map((serve) => (
          <div key={serve.serve_id} className="card hover:shadow-lg transition-shadow duration-200">
            {/* Video Preview */}
            <div className="relative bg-gray-100 rounded-lg overflow-hidden mb-4 aspect-video">
              <video
                src={serve.video_url}
                className="w-full h-full object-cover"
                controls
                preload="metadata"
              />
              <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                Serve #{serve.serve_id + 1}
              </div>
            </div>

            {/* Serve Info */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Serve {serve.serve_id + 1}</h3>
                <span className={`text-sm font-medium ${getConfidenceColor(serve.confidence)}`}>
                  {Math.round(serve.confidence * 100)}% confidence
                </span>
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{formatDuration(serve.duration)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Play className="w-4 h-4" />
                  <span>Frames {serve.start_frame}-{serve.end_frame}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <button
                  onClick={() => setSelectedServe(serve)}
                  className="flex-1 btn-secondary text-sm flex items-center justify-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  View Details
                </button>
                <button
                  onClick={() => handleDownload(serve)}
                  disabled={isDownloading === serve.serve_id}
                  className="btn-primary text-sm flex items-center justify-center gap-2"
                >
                  {isDownloading === serve.serve_id ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Downloading...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      Download
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Serve Details Modal */}
      {selectedServe && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">
                  Serve {selectedServe.serve_id + 1} Details
                </h3>
                <button
                  onClick={() => setSelectedServe(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Video Player */}
                <div>
                  <video
                    src={selectedServe.video_url}
                    className="w-full rounded-lg"
                    controls
                    autoPlay
                  />
                </div>

                {/* Details */}
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-500">Confidence</div>
                      <div className={`text-lg font-semibold ${getConfidenceColor(selectedServe.confidence)}`}>
                        {Math.round(selectedServe.confidence * 100)}%
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-500">Duration</div>
                      <div className="text-lg font-semibold text-gray-900">
                        {formatDuration(selectedServe.duration)}
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-sm text-gray-500 mb-2">Frame Range</div>
                    <div className="text-sm text-gray-900">
                      Start: {selectedServe.start_frame} | End: {selectedServe.end_frame}
                    </div>
                  </div>

                  <div className="pt-4">
                    <button
                      onClick={() => handleDownload(selectedServe)}
                      disabled={isDownloading === selectedServe.serve_id}
                      className="w-full btn-primary flex items-center justify-center gap-2"
                    >
                      {isDownloading === selectedServe.serve_id ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          Downloading...
                        </>
                      ) : (
                        <>
                          <Download className="w-4 h-4" />
                          Download Serve Video
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
