import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileVideo, AlertCircle } from 'lucide-react';
import { useAppStore } from '../store';
import { api } from '../api';

export const VideoUpload: React.FC = () => {
  const { config, setUploading, setError, setCurrentTask, setProcessing, isUploading, error, setAnalysisStatus } = useAppStore();
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Enhanced file validation function
  const validateVideoFile = (file: File): { isValid: boolean; error?: string } => {
    // Check file extension first (more reliable)
    const allowedExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedExtensions.includes(fileExtension)) {
      return { 
        isValid: false, 
        error: 'Please upload a valid video file (MP4, AVI, MOV, MKV, or WebM)' 
      };
    }
    
    // Additional MIME type check as secondary validation
    const allowedMimeTypes = [
      'video/mp4', 'video/mp4v-es', 'video/x-m4v',  // MP4 variants
      'video/avi', 'video/x-msvideo',               // AVI variants
      'video/quicktime', 'video/x-ms-wmv',          // MOV and WMV
      'video/x-matroska', 'video/webm'              // MKV and WebM
    ];
    
    if (file.type && !allowedMimeTypes.includes(file.type)) {
      console.warn(`Unexpected MIME type for ${file.name}: ${file.type}`);
      // Don't reject based on MIME type alone, just log warning
    }
    
    return { isValid: true };
  };

  // Enhanced file size validation
  const validateFileSize = (file: File): { isValid: boolean; error?: string } => {
    const maxSize = 500 * 1024 * 1024; // 500MB
    const maxSizeMB = 500;
    
    if (file.size > maxSize) {
      const fileSizeMB = Math.round(file.size / (1024 * 1024));
      return {
        isValid: false,
        error: `File size (${fileSizeMB}MB) exceeds maximum allowed size (${maxSizeMB}MB)`
      };
    }
    
    return { isValid: true };
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      return;
    }

    const file = acceptedFiles[0];
    setSelectedFile(file);
    
    // Validate file type
    const typeValidation = validateVideoFile(file);
    if (!typeValidation.isValid) {
      setError(typeValidation.error!);
      return;
    }
    
    // Validate file size
    const sizeValidation = validateFileSize(file);
    if (!sizeValidation.isValid) {
      setError(sizeValidation.error!);
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setUploadProgress(0);
      
      // Simulate progress for now (since fetch doesn't support progress)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);
      
      // Use the existing API function
      const response = await api.uploadVideo(file, config);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setCurrentTask(response.task_id);
      setProcessing(true);
      
      // Initialize analysis status to start polling
      setAnalysisStatus({
        task_id: response.task_id,
        status: 'pending',
        progress: 0.0,
        message: 'Video uploaded successfully, starting analysis...'
      });
      
      setSelectedFile(null); // Clear selected file after successful upload
      
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [config, setUploading, setError, setCurrentTask, setProcessing, setAnalysisStatus]);

  // Progress bar component
  const UploadProgress: React.FC<{ progress: number; uploading: boolean }> = ({ 
    progress, 
    uploading 
  }) => {
    if (!uploading) return null;
    
    return (
      <div className="mt-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Uploading...</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-primary-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    );
  };

  // File info component
  const FileInfo: React.FC<{ file: File | null }> = ({ file }) => {
    if (!file) return null;
    
    const formatFileSize = (bytes: number): string => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    return (
      <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
        <div className="flex items-center">
          <FileVideo className="w-5 h-5 text-gray-500 mr-2" />
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-700">{file.name}</p>
            <p className="text-xs text-gray-500">
              {formatFileSize(file.size)} • {file.type || 'Unknown type'}
            </p>
          </div>
        </div>
      </div>
    );
  };

  // Error message component
  const ErrorMessage: React.FC<{ error: string | null }> = ({ error }) => {
    if (!error) return null;
    
    return (
      <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700 text-sm">{error}</span>
        </div>
      </div>
    );
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    },
    multiple: false,
    maxSize: 500 * 1024 * 1024 // 500MB
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
            border-2 border-dashed rounded-lg p-8 cursor-pointer transition-all duration-200
            ${isDragActive 
              ? 'border-primary-500 bg-primary-50 scale-105' 
              : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50 hover:scale-102'
            }
          `}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center">
            <Upload className="w-12 h-12 text-gray-400 mb-4" />
            
            <div className="text-center">
              {isDragActive ? (
                <p className="text-primary-600 font-medium">Drop the video here...</p>
              ) : (
                <>
                  <p className="text-gray-700 font-medium mb-2">
                    Drag & drop your video here, or click to browse
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports MP4, AVI, MOV, MKV, WebM (max 500MB)
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
        
        <FileInfo file={selectedFile} />
        <UploadProgress progress={uploadProgress} uploading={isUploading} />
        <ErrorMessage error={error} />
        
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
