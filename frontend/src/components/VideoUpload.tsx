import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileVideo, AlertCircle } from 'lucide-react';
import { useAppStore } from '../store';
import { api } from '../api';

export const VideoUpload: React.FC = () => {
  const { config, setUploading, setError, setCurrentTask, setProcessing } = useAppStore();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Validate file type
    const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a valid video file (MP4, AVI, MOV, or MKV)');
      return;
    }

    // Validate file size (100MB limit)
    if (file.size > 100 * 1024 * 1024) {
      setError('File size must be less than 100MB');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      
      const response = await api.uploadVideo(file, config);
      setCurrentTask(response.task_id);
      setProcessing(true);
      
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [config, setUploading, setError, setCurrentTask, setProcessing]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  return (
    <div className="card">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Upload Tennis Serve Video</h2>
        <p className="text-gray-600 mb-6">
          Upload a video of your tennis serve to analyze technique and extract serve segments.
        </p>
        
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 cursor-pointer transition-colors duration-200
            ${isDragActive && !isDragReject 
              ? 'border-primary-500 bg-primary-50' 
              : isDragReject 
                ? 'border-red-500 bg-red-50' 
                : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            }
          `}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center">
            {isDragReject ? (
              <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
            ) : (
              <Upload className="w-12 h-12 text-gray-400 mb-4" />
            )}
            
            <div className="text-center">
              {isDragActive && !isDragReject ? (
                <p className="text-primary-600 font-medium">Drop the video here...</p>
              ) : isDragReject ? (
                <p className="text-red-600 font-medium">Invalid file type</p>
              ) : (
                <>
                  <p className="text-gray-700 font-medium mb-2">
                    Drag & drop your video here, or click to browse
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports MP4, AVI, MOV, MKV (max 100MB)
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
        
        <div className="mt-6 text-sm text-gray-500">
          <div className="flex items-center justify-center gap-2 mb-2">
            <FileVideo className="w-4 h-4" />
            <span>Recommended: Side view of serve motion</span>
          </div>
          <p>For best results, ensure the player is clearly visible and well-lit.</p>
        </div>
      </div>
    </div>
  );
};
