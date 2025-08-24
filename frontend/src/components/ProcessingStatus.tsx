import React, { useEffect, useRef } from 'react';
import { Loader2, CheckCircle, XCircle, Play } from 'lucide-react';
import { useAppStore } from '../store';
import { api } from '../api';

interface ProcessingStep {
  name: string;
  progress: number;
  message: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

const ProcessingSteps: React.FC<{ steps: ProcessingStep[] }> = ({ steps }) => {
  return (
    <div className="space-y-4">
      {steps.map((step, index) => (
        <div key={index} className="flex items-center space-x-3">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
            step.status === 'completed' ? 'bg-green-500' :
            step.status === 'processing' ? 'bg-blue-500' :
            step.status === 'failed' ? 'bg-red-500' : 'bg-gray-300'
          }`}>
            {step.status === 'completed' ? '✓' :
             step.status === 'processing' ? '⟳' :
             step.status === 'failed' ? '✗' : index + 1}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium">{step.name}</p>
            <p className="text-xs text-gray-500">{step.message}</p>
          </div>
          {step.status === 'processing' && (
            <div className="w-16 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${step.progress}%` }}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

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
          setAnalysisResults(results);
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

  // Create processing steps based on progress
  const createProcessingSteps = (): ProcessingStep[] => {
    const progress = analysisStatus.progress;
    const status = analysisStatus.status;
    
    const steps: ProcessingStep[] = [
      {
        name: "Loading video and initializing analysis",
        progress: progress >= 0.1 ? 100 : 0,
        message: "Preparing video for analysis...",
        status: progress >= 0.1 ? 'completed' : (progress > 0 ? 'processing' : 'pending')
      },
      {
        name: "Video quality assessment",
        progress: progress >= 0.2 ? 100 : Math.max(0, (progress - 0.1) * 1000),
        message: "Analyzing video quality and properties...",
        status: progress >= 0.2 ? 'completed' : (progress > 0.1 ? 'processing' : 'pending')
      },
      {
        name: "Video optimization",
        progress: progress >= 0.3 ? 100 : Math.max(0, (progress - 0.2) * 1000),
        message: "Optimizing video for processing...",
        status: progress >= 0.3 ? 'completed' : (progress > 0.2 ? 'processing' : 'pending')
      },
      {
        name: "Serve detection",
        progress: progress >= 0.4 ? 100 : Math.max(0, (progress - 0.3) * 1000),
        message: "Detecting serves in video...",
        status: progress >= 0.4 ? 'completed' : (progress > 0.3 ? 'processing' : 'pending')
      },
      {
        name: "Pose estimation",
        progress: progress >= 0.6 ? 100 : Math.max(0, (progress - 0.4) * 500),
        message: "Estimating player pose and landmarks...",
        status: progress >= 0.6 ? 'completed' : (progress > 0.4 ? 'processing' : 'pending')
      },
      {
        name: "Serve segmentation",
        progress: progress >= 0.8 ? 100 : Math.max(0, (progress - 0.6) * 500),
        message: "Extracting serve segments...",
        status: progress >= 0.8 ? 'completed' : (progress > 0.6 ? 'processing' : 'pending')
      },
      {
        name: "Creating output archive",
        progress: progress >= 0.9 ? 100 : Math.max(0, (progress - 0.8) * 1000),
        message: "Creating output archive...",
        status: progress >= 0.9 ? 'completed' : (progress > 0.8 ? 'processing' : 'pending')
      }
    ];

    if (status === 'failed') {
      // Mark all steps after the failed one as failed
      const failedIndex = steps.findIndex(step => step.status === 'processing');
      if (failedIndex !== -1) {
        steps[failedIndex].status = 'failed';
        for (let i = failedIndex + 1; i < steps.length; i++) {
          steps[i].status = 'pending';
        }
      }
    }

    return steps;
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
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Overall Progress</span>
          <span>{Math.round(analysisStatus.progress * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-300 ${getProgressColor()}`}
            style={{ width: `${analysisStatus.progress * 100}%` }}
          />
        </div>
      </div>

      {/* Enhanced Processing Steps */}
      {analysisStatus.status === 'processing' && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Processing Steps</h4>
          <ProcessingSteps steps={createProcessingSteps()} />
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
            <p>• ZIP archive is ready for download</p>
          </div>
        </div>
      )}
    </div>
  );
};
