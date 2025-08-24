# UX Plan V2 - Video Upload Fix and Enhanced User Experience

**Date**: January 27, 2025  
**Version**: 2.1.0  
**Previous Version**: v2.0.0 (Serve Segmentation Implementation)

## 🎯 Overview

This plan addresses the critical video upload issue where MP4 files are being rejected as "invalid file type" and outlines comprehensive improvements to enhance the user experience of the Tennis Serve Analysis web application.

## 🚨 Critical Issue: Video Upload File Type Validation

### **Problem Description**
- Users are unable to upload MP4 files due to incorrect file type validation
- The frontend is checking `file.type` (MIME type) instead of file extension
- MP4 files can have various MIME types: `video/mp4`, `video/mp4v-es`, `video/x-m4v`, etc.
- Browser MIME type detection is inconsistent across different systems

### **Root Cause Analysis**
1. **Frontend Validation Logic**: `VideoUpload.tsx` uses `file.type` for validation
2. **MIME Type Inconsistency**: MP4 files may not always have `video/mp4` MIME type
3. **Browser Differences**: Different browsers report different MIME types for the same file
4. **System Variations**: Operating system affects MIME type detection

## �� Required Changes

### **1. Frontend File Validation Fix**

#### **File**: `frontend/src/components/VideoUpload.tsx`

**Current Problematic Code** (lines 18-22):
```typescript
// Validate file type
const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska'];
if (!allowedTypes.includes(file.type)) {
  setError('Please upload a valid video file (MP4, AVI, MOV, or MKV)');
  return;
}
```

**Required Changes**:
```typescript
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

// Update onDrop function
const onDrop = useCallback(async (acceptedFiles: File[]) => {
  if (acceptedFiles.length === 0) return;

  const file = acceptedFiles[0];
  
  // Use enhanced validation
  const validation = validateVideoFile(file);
  if (!validation.isValid) {
    setError(validation.error!);
    return;
  }

  // Rest of the function remains the same...
}, [config, setUploading, setError, setCurrentTask, setProcessing]);
```

#### **File**: `frontend/src/components/VideoUpload.tsx` (Dropzone Configuration)

**Update dropzone accept configuration** (lines 35-40):
```typescript
const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
  onDrop,
  accept: {
    'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
  },
  multiple: false,
  maxSize: 100 * 1024 * 1024, // 100MB
  validator: (file) => {
    const validation = validateVideoFile(file);
    return validation.isValid ? null : new Error(validation.error!);
  }
});
```

### **2. Backend File Validation Enhancement**

#### **File**: `src/serve_ai_analysis/web/api.py`

**Current Code** (lines 108-115):
```python
# Validate file type
allowed_extensions = {".mp4", ".avi", ".mov", ".mkv"}
file_ext = Path(file.filename).suffix.lower()
if file_ext not in allowed_extensions:
    raise HTTPException(
        status_code=400, 
        detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
    )
```

**Required Changes**:
```python
# Enhanced file validation
def validate_video_file(file: UploadFile) -> bool:
    """Validate uploaded video file."""
    if not file.filename:
        return False
    
    # Check file extension
    allowed_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        return False
    
    # Additional MIME type validation (optional)
    allowed_mime_types = {
        "video/mp4", "video/mp4v-es", "video/x-m4v",
        "video/avi", "video/x-msvideo",
        "video/quicktime", "video/x-ms-wmv",
        "video/x-matroska", "video/webm"
    }
    
    if file.content_type and file.content_type not in allowed_mime_types:
        # Log warning but don't reject
        print(f"Warning: Unexpected MIME type for {file.filename}: {file.content_type}")
    
    return True

# Update upload endpoint
@app.post("/upload", response_model=dict)
async def upload_video(
    file: UploadFile = File(...),
    config: AnalysisRequest = None
):
    """Upload video and start analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Use enhanced validation
    if not validate_video_file(file):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Allowed: MP4, AVI, MOV, MKV, WebM"
        )
    
    # Rest of the function remains the same...
```

### **3. Error Handling Improvements**

#### **File**: `frontend/src/components/VideoUpload.tsx`

**Add better error display**:
```typescript
// Add error display component
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

// Update component JSX to include error display
return (
  <div className="card">
    {/* ... existing content ... */}
    
    <ErrorMessage error={error} />
    
    {/* ... rest of content ... */}
  </div>
);
```

### **4. File Size Validation Enhancement**

#### **File**: `frontend/src/components/VideoUpload.tsx`

**Improve file size validation**:
```typescript
// Enhanced file size validation
const validateFileSize = (file: File): { isValid: boolean; error?: string } => {
  const maxSize = 100 * 1024 * 1024; // 100MB
  const maxSizeMB = 100;
  
  if (file.size > maxSize) {
    const fileSizeMB = Math.round(file.size / (1024 * 1024));
    return {
      isValid: false,
      error: `File size (${fileSizeMB}MB) exceeds maximum allowed size (${maxSizeMB}MB)`
    };
  }
  
  return { isValid: true };
};

// Update onDrop function to include size validation
const onDrop = useCallback(async (acceptedFiles: File[]) => {
  if (acceptedFiles.length === 0) return;

  const file = acceptedFiles[0];
  
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

  // Rest of the function...
}, [config, setUploading, setError, setCurrentTask, setProcessing]);
```

## 🎨 Enhanced User Experience Features

### **1. Upload Progress Indicator**

#### **File**: `frontend/src/components/VideoUpload.tsx`

**Add upload progress tracking**:
```typescript
// Add progress state
const [uploadProgress, setUploadProgress] = useState<number>(0);

// Update onDrop function with progress tracking
const onDrop = useCallback(async (acceptedFiles: File[]) => {
  // ... validation code ...

  try {
    setUploading(true);
    setError(null);
    setUploadProgress(0);
    
    // Create FormData with progress tracking
    const formData = new FormData();
    formData.append('file', file);
    formData.append('config', JSON.stringify(config));
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const progress = (event.loaded / event.total) * 100;
        setUploadProgress(progress);
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        setCurrentTask(response.task_id);
        setProcessing(true);
      } else {
        setError(`Upload failed: ${xhr.statusText}`);
      }
    });
    
    xhr.addEventListener('error', () => {
      setError('Upload failed. Please try again.');
    });
    
    xhr.open('POST', '/api/upload');
    xhr.send(formData);
    
  } catch (error) {
    setError(error instanceof Error ? error.message : 'Upload failed');
  } finally {
    setUploading(false);
    setUploadProgress(0);
  }
}, [config, setUploading, setError, setCurrentTask, setProcessing]);
```

**Add progress bar component**:
```typescript
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
```

### **2. File Preview and Information**

#### **File**: `frontend/src/components/VideoUpload.tsx`

**Add file information display**:
```typescript
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
```

### **3. Enhanced Dropzone Visual Feedback**

#### **File**: `frontend/src/components/VideoUpload.tsx`

**Improve dropzone styling**:
```typescript
// Enhanced dropzone styling
<div
  {...getRootProps()}
  className={`
    border-2 border-dashed rounded-lg p-8 cursor-pointer transition-all duration-200
    ${isDragActive && !isDragReject 
      ? 'border-primary-500 bg-primary-50 scale-105' 
      : isDragReject 
        ? 'border-red-500 bg-red-50 scale-105' 
        : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50 hover:scale-102'
    }
  `}
>
  {/* ... existing content ... */}
</div>
```

## 🧪 Testing Requirements

### **1. File Upload Testing**

**Test Cases**:
1. **Valid MP4 files** with different MIME types:
   - `video/mp4`
   - `video/mp4v-es`
   - `video/x-m4v`
   - Empty MIME type

2. **Other video formats**:
   - AVI files
   - MOV files
   - MKV files
   - WebM files

3. **Invalid files**:
   - Text files with .mp4 extension
   - Image files
   - Audio files
   - Files without extensions

4. **File size testing**:
   - Files under 100MB
   - Files exactly 100MB
   - Files over 100MB

### **2. Browser Compatibility Testing**

**Test Browsers**:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

**Test Scenarios**:
- Drag and drop functionality
- File picker dialog
- MIME type detection
- File size reporting

### **3. Error Handling Testing**

**Test Error Scenarios**:
- Network failures during upload
- Server errors
- Invalid file types
- File size exceeded
- Missing files

## 📋 Implementation Checklist

### **Phase 1: Critical Fixes (Priority 1)**
- [ ] Update frontend file validation logic in `VideoUpload.tsx`
- [ ] Update backend file validation in `api.py`
- [ ] Test MP4 file uploads across different browsers
- [ ] Verify error messages are clear and helpful

### **Phase 2: Enhanced UX (Priority 2)**
- [ ] Add upload progress indicator
- [ ] Implement file information display
- [ ] Enhance dropzone visual feedback
- [ ] Add comprehensive error handling

### **Phase 3: Testing and Polish (Priority 3)**
- [ ] Complete browser compatibility testing
- [ ] Test all supported file formats
- [ ] Validate error handling scenarios
- [ ] Performance testing with large files

## 📈 Success Metrics

### **Technical Metrics**
- ✅ 100% MP4 file upload success rate
- ✅ Clear error messages for invalid files
- ✅ Proper file size validation
- ✅ Cross-browser compatibility

### **User Experience Metrics**
- ✅ Intuitive upload interface
- ✅ Real-time progress feedback
- ✅ Helpful error messages
- ✅ Smooth drag-and-drop experience

## 🔮 Future Enhancements

### **Planned Features**
1. **Video Preview**: Show thumbnail before upload
2. **Batch Upload**: Support multiple video uploads
3. **Advanced Validation**: Check video codec compatibility
4. **Upload Resume**: Resume interrupted uploads
5. **Cloud Storage**: Direct upload to cloud storage

### **Performance Improvements**
1. **Chunked Upload**: Large file upload optimization
2. **Compression**: Client-side video compression
3. **Caching**: Upload progress caching
4. **Retry Logic**: Automatic retry on failure

---

**Next Version Target**: v2.2.0 - Advanced Video Processing and Analysis  
**Estimated Release**: Q1 2025
