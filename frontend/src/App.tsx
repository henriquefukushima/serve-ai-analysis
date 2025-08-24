import { useState } from 'react';
import { Activity, Settings, RotateCcw } from 'lucide-react';
import { VideoUpload } from './components/VideoUpload';
import { AnalysisConfig } from './components/AnalysisConfig';
import { ProcessingStatus } from './components/ProcessingStatus';
import { ResultsDownload } from './components/ResultsDownload';
import { useAppStore } from './store';

function App() {
  const { 
    currentTaskId, 
    analysisResults, 
    isProcessing, 
    error, 
    reset 
  } = useAppStore();
  
  const [configExpanded, setConfigExpanded] = useState(false);

  const handleReset = () => {
    reset();
    setConfigExpanded(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Activity className="w-8 h-8 text-primary-600" />
              <h1 className="text-xl font-bold text-gray-900">Tennis Serve Analysis</h1>
            </div>
            
            <div className="flex items-center gap-4">
              <button
                onClick={() => setConfigExpanded(!configExpanded)}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <Settings className="w-5 h-5" />
                <span className="hidden sm:inline">Settings</span>
              </button>
              
              {(currentTaskId || analysisResults) && (
                <button
                  onClick={handleReset}
                  className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
                  title="Start over"
                >
                  <RotateCcw className="w-5 h-5" />
                  <span className="hidden sm:inline">New Analysis</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">!</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
                <button
                  onClick={() => useAppStore.getState().setError(null)}
                  className="text-red-400 hover:text-red-600"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {/* Upload Section */}
          {!currentTaskId && !analysisResults && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <VideoUpload />
              </div>
              <div>
                <AnalysisConfig 
                  isExpanded={configExpanded} 
                  onToggle={() => setConfigExpanded(!configExpanded)} 
                />
              </div>
            </div>
          )}

          {/* Processing Status */}
          {currentTaskId && isProcessing && (
            <ProcessingStatus />
          )}

          {/* Results */}
          {analysisResults && currentTaskId && (
            <ResultsDownload />
          )}

          {/* Start Over Button */}
          {analysisResults && (
            <div className="text-center pt-8">
              <button
                onClick={handleReset}
                className="btn-primary flex items-center gap-2 mx-auto"
              >
                <RotateCcw className="w-5 h-5" />
                Analyze Another Video
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p className="text-sm">
              Tennis Serve Analysis v2.0.0 - Advanced AI-powered serve detection and analysis
            </p>
            <p className="text-xs mt-2 text-gray-500">
              Built with React, FastAPI, and MediaPipe for accurate pose estimation and serve detection
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
