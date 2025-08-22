import React from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useAppStore } from '../store';

interface AnalysisConfigProps {
  isExpanded: boolean;
  onToggle: () => void;
}

export const AnalysisConfig: React.FC<AnalysisConfigProps> = ({ isExpanded, onToggle }) => {
  const { config, setConfig } = useAppStore();

  return (
    <div className="card">
      <button
        onClick={onToggle}
        className="flex items-center justify-between w-full text-left mb-4"
      >
        <h3 className="text-lg font-semibold text-gray-900">Analysis Configuration</h3>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-500" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-500" />
        )}
      </button>

      {isExpanded && (
        <div className="space-y-6">
          {/* Player Handedness */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Player Handedness
            </label>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="handedness"
                  value="right"
                  checked={config.player_handedness === 'right'}
                  onChange={(e) => setConfig({ player_handedness: e.target.value as 'right' | 'left' })}
                  className="mr-2"
                />
                Right-handed
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="handedness"
                  value="left"
                  checked={config.player_handedness === 'left'}
                  onChange={(e) => setConfig({ player_handedness: e.target.value as 'right' | 'left' })}
                  className="mr-2"
                />
                Left-handed
              </label>
            </div>
          </div>

          {/* Confidence Threshold */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confidence Threshold: {config.confidence_threshold}
            </label>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={config.confidence_threshold}
              onChange={(e) => setConfig({ confidence_threshold: parseFloat(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0.1 (More detections)</span>
              <span>1.0 (Higher accuracy)</span>
            </div>
          </div>

          {/* Duration Limits */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Serve Duration (seconds)
              </label>
              <input
                type="number"
                min="0.5"
                max="10.0"
                step="0.1"
                value={config.min_serve_duration}
                onChange={(e) => setConfig({ min_serve_duration: parseFloat(e.target.value) })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Serve Duration (seconds)
              </label>
              <input
                type="number"
                min="1.0"
                max="20.0"
                step="0.1"
                value={config.max_serve_duration}
                onChange={(e) => setConfig({ max_serve_duration: parseFloat(e.target.value) })}
                className="input-field"
              />
            </div>
          </div>

          {/* Processing Options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Processing Options
            </label>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.optimize_video}
                  onChange={(e) => setConfig({ optimize_video: e.target.checked })}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium">Optimize video for processing</div>
                  <div className="text-sm text-gray-500">Reduces file size and improves processing speed</div>
                </div>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.include_landmarks}
                  onChange={(e) => setConfig({ include_landmarks: e.target.checked })}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium">Include pose landmarks overlay</div>
                  <div className="text-sm text-gray-500">Adds pose tracking visualization to output videos</div>
                </div>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.extract_segments}
                  onChange={(e) => setConfig({ extract_segments: e.target.checked })}
                  className="mr-3"
                />
                <div>
                  <div className="font-medium">Extract serve segments only</div>
                  <div className="text-sm text-gray-500">Creates individual video clips for each detected serve</div>
                </div>
              </label>
            </div>
          </div>

          {/* Reset to Defaults */}
          <div className="pt-4 border-t border-gray-200">
            <button
              onClick={() => setConfig({
                confidence_threshold: 0.7,
                min_serve_duration: 1.5,
                max_serve_duration: 8.0,
                optimize_video: true,
                include_landmarks: true,
                extract_segments: true,
                player_handedness: 'right',
              })}
              className="btn-secondary text-sm"
            >
              Reset to Defaults
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
