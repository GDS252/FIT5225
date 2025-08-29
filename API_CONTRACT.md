# Frontend-Backend API Contract

This document defines the exact API contract between the frontend and backend Lambda functions.

## Authentication
All API calls (except presigned URL generation) require JWT authentication via Authorization header:
```
Authorization: Bearer <jwt-token>
```

## 1. File Upload Flow

### 1.1 Get Presigned URL
**Frontend Call:**
```javascript
POST /files
Content-Type: application/json

{
  "fileName": "bird-photo.jpg",
  "fileType": "image/jpeg", 
  "fileSize": 2048576
}
```

**Backend Response:**
```json
{
  "url": "https://bucket.s3.amazonaws.com/...",
  "fields": {
    "key": "uploads/user123/uuid/bird-photo.jpg",
    "policy": "...",
    "signature": "..."
  },
  "fileId": "uuid-generated-id"
}
```

### 1.2 Upload to S3
**Frontend Action:**
- Upload directly to S3 using presigned URL
- S3 automatically triggers SNS -> Lambda processing
- **NO manual notification needed**

## 2. File Operations

### 2.1 Get File List
**Frontend Call:**
```javascript
GET /files
GET /files?limit=6&sort=recent
```

**Backend Response:**
```json
{
  "files": [
    {
      "id": "file-uuid",
      "filename": "bird-photo.jpg",
      "url": "https://cloudfront.../optimized/...",
      "thumbnailUrl": "https://cloudfront.../thumbnails/...",
      "uploadedAt": "2024-01-15T10:30:00Z",
      "predictions": [
        {
          "label": "House Sparrow",
          "confidence": 0.85
        }
      ],
      "tags": ["small bird", "garden bird"]
    }
  ],
  "total": 42
}
```

### 2.2 Search by Tags
**Frontend Call:**
```javascript
POST /query/by-tags
Content-Type: application/json

{
  "tags": ["sparrow", "small bird"],
  "confidence": 0.7,
  "limit": 50
}
```

**Backend Response:**
```json
{
  "files": [...], // Same format as Get File List
  "total": 15,
  "searchCriteria": {
    "tags": ["sparrow", "small bird"],
    "confidence": 0.7
  }
}
```

### 2.3 Update Tags
**Frontend Call:**
```javascript
POST /tags/update
Content-Type: application/json

{
  "fileId": "file-uuid",
  "tags": ["updated tag 1", "updated tag 2"]
}
```

**Backend Response:**
```json
{
  "success": true,
  "fileId": "file-uuid",
  "updatedTags": ["updated tag 1", "updated tag 2"]
}
```

### 2.4 Delete Files
**Frontend Call:**
```javascript
POST /admin/files/delete
Content-Type: application/json

{
  "urls": [
    "https://cloudfront.../optimized/file1.jpg",
    "https://cloudfront.../optimized/file2.jpg"
  ]
}
```

**Backend Response:**
```json
{
  "success": true,
  "deletedFiles": 2,
  "results": [
    {
      "url": "https://cloudfront.../optimized/file1.jpg",
      "status": "deleted"
    },
    {
      "url": "https://cloudfront.../optimized/file2.jpg", 
      "status": "deleted"
    }
  ]
}
```

## 3. Error Responses

All endpoints should return consistent error formats:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file type. Only images are allowed.",
    "details": {
      "field": "fileType",
      "received": "application/pdf"
    }
  }
}
```

**Common Error Codes:**
- `VALIDATION_ERROR`: Invalid input parameters
- `AUTHENTICATION_ERROR`: Invalid or missing JWT token
- `AUTHORIZATION_ERROR`: User not authorized for this operation
- `NOT_FOUND`: Requested resource not found
- `INTERNAL_ERROR`: Server-side error

## 4. Frontend Implementation Notes

### 4.1 Upload Flow (CORRECTED)
```javascript
// ✅ CORRECT: 2-step process
const handleUpload = async (file) => {
  // Step 1: Get presigned URL
  const response = await apiClient.post('/files', {
    fileName: file.name,
    fileType: file.type,
    fileSize: file.size
  })
  
  // Step 2: Upload to S3 (triggers automatic processing)
  const formData = new FormData()
  Object.entries(response.data.fields).forEach(([key, value]) => {
    formData.append(key, value)
  })
  formData.append('file', file)
  
  await axios.post(response.data.url, formData)
  
  // ✅ DONE! Backend handles everything automatically
  // ❌ NO manual '/files/process' call needed
}
```

### 4.2 Error Handling
```javascript
// Handle API errors consistently
try {
  const response = await apiClient.post('/endpoint', data)
  // Handle success
} catch (error) {
  if (error.response?.data?.error) {
    // Backend error format
    ElMessage.error(error.response.data.error.message)
  } else {
    // Network or other error
    ElMessage.error('Operation failed. Please try again.')
  }
}
```

## 5. Backend Lambda Requirements

To support this frontend, your Lambda functions must:

1. **POST /files**: Generate presigned URLs and register file metadata
2. **GET /files**: Return file lists with proper pagination and sorting
3. **POST /query/by-tags**: Search files by tags with confidence filtering
4. **POST /tags/update**: Update tags for specific files
5. **POST /admin/files/delete**: Delete files from S3 and database
6. **S3 Trigger**: Automatically process uploaded files (generate thumbnails, AI tagging)

Each Lambda should properly handle CORS, authentication, and return consistent response formats.
