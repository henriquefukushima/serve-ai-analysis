import React, { useEffect, useRef } from 'react';
import { Loader2, CheckCircle, XCircle, Play } from 'lucide-react';
import { useAppStore } from '../store';
import { api } from '../api';

export const ProcessingStatus: React.FC = () => {
  const { 
    currentTaskId, 
    analysisStatus, 
    setAnalysisStatus, 
    setAnalysisResults, 
    setProcessing,
    setError 
  } = useAppStore();
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!currentTaskId || !analysisStatus) return;

    // Poll for status updates
    const pollStatus = async () => {
      try {
        const status = await api.getAnalysisStatus(currentTaskId);
        setAnalysisStatus(status);

        if (status.status === 'completed') {
          // Get results
          const results = await api.getAnalysisResults(currentTaskId);
          setAnalysisResults(results.serves);
          setProcessing(false);
          
          // Clear interval
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        } else if (status.status === 'failed') {
          setError(status.error || 'Analysis failed');
          setProcessing(false);
          
          // Clear interval
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        }
      } catch (error) {
        setError(error instanceof Error ? error.message : 'Failed to check status');
        setProcessing(false);
        
        // Clear interval
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    };

    // Poll every 2 seconds
    intervalRef.current = setInterval(pollStatus, 2000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [currentTaskId, analysisStatus, setAnalysisStatus, setAnalysisResults, setProcessing, setError]);

  if (!analysisStatus) return null;

  const getStatusIcon = () => {
    switch (analysisStatus.status) {
      case 'pending':
        return <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />;
      case 'processing':
        return <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />;
      default:
        return <Play className="w-6 h-6 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    switch (analysisStatus.status) {
      case 'pending':
      case 'processing':
        return 'text-blue-600';
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getProgressColor = () => {
    switch (analysisStatus.status) {
      case 'pending':
      case 'processing':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-300';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center gap-4 mb-4">
        {getStatusIcon()}
        <div className="flex-1">
          <h3 className={`font-semibold ${getStatusColor()}`}>
            {analysisStatus.status === 'pending' && 'Preparing Analysis...'}
            {analysisStatus.status === 'processing' && 'Processing Video...'}
            {analysisStatus.status === 'completed' && 'Analysis Complete!'}
            {analysisStatus.status === 'failed' && 'Analysis Failed'}
          </h3>
          <p className="text-sm text-gray-600 mt-1">{analysisStatus.message}</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{Math.round(analysisStatus.progress * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${getProgressColor()}`}
            style={{ width: `${analysisStatus.progress * 100}%` }}
          />
        </div>
      </div>

      {/* Processing Steps */}
      {analysisStatus.status === 'processing' && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${analysisStatus.progress >= 0.1 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={analysisStatus.progress >= 0.1 ? 'text-green-600' : 'text-gray-500'}>
              Video quality assessment
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${analysisStatus.progress >= 0.2 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={analysisStatus.progress >= 0.2 ? 'text-green-600' : 'text-gray-500'}>
              Video optimization
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${analysisStatus.progress >= 0.3 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={analysisStatus.progress >= 0.3 ? 'text-green-600' : 'text-gray-500'}>
              Pose detection
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${analysisStatus.progress >= 0.5 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={analysisStatus.progress >= 0.5 ? 'text-green-600' : 'text-gray-500'}>
              Ball trajectory detection
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${analysisStatus.progress >= 0.7 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={analysisStatus.progress >= 0.7 ? 'text-green-600' : 'text-gray-500'}>
              Serve identification
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${analysisStatus.progress >= 0.9 ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span className={analysisStatus.progress >= 0.9 ? 'text-green-600' : 'text-gray-500'}>
              Extracting serve clips
            </span>
          </div>
        </div>
      )}

      {/* Error Display */}
      {analysisStatus.status === 'failed' && analysisStatus.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-700">{analysisStatus.error}</p>
        </div>
      )}

      {/* Success Summary */}
      {analysisStatus.status === 'completed' && analysisStatus.results && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <h4 className="font-medium text-green-800 mb-2">Analysis Results</h4>
          <div className="text-sm text-green-700">
            <p>• Found {analysisStatus.results.total_serves} serve(s)</p>
            <p>• Processing completed successfully</p>
            <p>• Serve clips are ready for download</p>
          </div>
        </div>
      )}
    </div>
  );
};
