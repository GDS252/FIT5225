# Bird Recognition Frontend - AWS Integration Guide

## 🎯 **Completion Status**
✅ **All features completed and ready to connect with AWS backend APIs!**

## 🔧 **Pre-Deployment Configuration Checklist**

### **1. AWS Amplify Configuration**
Edit the `src/main.js` file and update the following configuration:

```javascript
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'ap-southeast-2_XXXXXXXXX',         // Replace with your User Pool ID
      userPoolClientId: 'xxxxxxxxxxxxxxxxxxxxxxxxxx', // Replace with your App Client ID
    }
  }
});
```

### **2. API Gateway Configuration**
Edit the `src/api/axios.js` file and update the API base URL:

```javascript
const apiClient = axios.create({
  baseURL: 'https://your-api-gateway-url.execute-api.ap-southeast-2.amazonaws.com/prod', // Replace with your API Gateway URL
});
```

## 📋 **API Endpoint Mapping**

The frontend has implemented the following API calls. Ensure your backend supports these endpoints:

### **Authentication Related**
- Direct AWS Cognito integration (no backend API needed)
- Automatic JWT token addition to all API requests

### **File Management**
- `GET /files` - Get all files list
- `GET /files?limit=6&sort=recent` - Get recently uploaded files
- `POST /files` - Get upload presigned URL
- `POST /files/process` - Notify backend of completed file upload

### **Query Functions**
- `POST /query/by-tags` - Search files by tags

### **Tag Management**
- `POST /tags/update` - Update file tags

### **Admin Functions**
- `POST /admin/files/delete` - Delete files

## 🚀 **Feature Overview**

### **✅ User Authentication Module**
- **Real AWS Cognito Integration**
- User registration + email verification
- Secure login/logout
- Route protection
- Automatic token management

### **✅ File Upload Module**
- **Real presigned URL upload**
- Drag & drop upload support
- Batch file processing
- Real-time upload progress
- File format validation (JPG, PNG, GIF, max 10MB)
- Error handling and retry

### **✅ Data Display Module**
- **Real API data fetching**
- Statistics display
- Search by tags (`POST /query/by-tags`)
- File sorting (by date/name)
- Responsive grid layout

### **✅ File Management Module**
- **Real tag updates** (`POST /tags/update`)
- **Real file deletion** (`POST /admin/files/delete`)
- Confirmation dialogs
- Instant UI updates

## 📱 **User Experience**

### **Complete User Flow**
1. **Register** → Email verification → **Login**
2. **Dashboard** → View statistics → Search files
3. **Upload page** → Drag files → View progress
4. **Manage files** → Edit tags → Delete files
5. **Logout** → Return to login page

### **Error Handling**
- Automatic network error retry
- User-friendly error messages
- Form validation
- Authentication state checking

## 🛠 **Development Commands**

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔐 **Security Features**

- Automatic JWT token management
- Route-level authentication protection
- HTTPS API communication
- Input validation and sanitization
- Error message sanitization

## 📊 **Performance Optimizations**

- Component lazy loading
- API response caching
- Image lazy loading
- Batch operation support
- Responsive design

## 🚨 **Important Reminders**

1. **Configure AWS Cognito**: Ensure User Pool and App Client are properly configured
2. **Configure API Gateway**: Ensure CORS settings are correct
3. **Test all API endpoints**: Ensure backend APIs respond correctly
4. **Check permissions**: Ensure S3 bucket permissions are configured correctly

## 📞 **Troubleshooting**

### Common Issues:

1. **Login Failure**
   - Check Cognito User Pool configuration
   - Verify App Client ID is correct

2. **Upload Failure**
   - Check API Gateway CORS settings
   - Verify presigned URL format

3. **API Call Failure**
   - Check network connection
   - Verify API Gateway URL
   - Check browser console for errors

## ✨ **Next Steps**

The frontend is fully ready to integrate with AWS backend!
You only need to:
1. Configure AWS Cognito User Pool
2. Deploy API Gateway
3. Update URLs and IDs in configuration files
4. Test the complete workflow

## 📋 **Configuration Requirements**

### **Required AWS Services**
- **AWS Cognito**: User Pool with email verification
- **API Gateway**: RESTful API endpoints
- **AWS S3**: File storage with presigned URL support
- **AWS Lambda**: Backend API functions (optional)

### **Frontend Dependencies**
- **Vue.js 3**: Modern reactive framework
- **Element Plus**: UI component library
- **AWS Amplify**: Authentication and API client
- **Axios**: HTTP client with JWT integration
- **Bootstrap**: Additional styling and icons

### **API Response Format**
Ensure your backend APIs return data in the expected format:

#### File List Response (`GET /files`):
```json
{
  "files": [
    {
      "id": "file-123",
      "filename": "bird.jpg",
      "url": "https://s3.amazonaws.com/bucket/bird.jpg",
      "thumbnailUrl": "https://s3.amazonaws.com/bucket/thumb/bird.jpg",
      "uploadedAt": "2024-01-01T00:00:00Z",
      "predictions": [
        {"label": "Cardinal", "confidence": 0.95}
      ],
      "tags": ["red bird", "garden"]
    }
  ]
}
```

#### Presigned URL Response (`POST /files`):
```json
{
  "url": "https://s3.amazonaws.com/bucket",
  "fields": {
    "key": "uploads/file-123.jpg",
    "policy": "...",
    "signature": "..."
  },
  "fileId": "file-123"
}
```

#### Search Response (`POST /query/by-tags`):
```json
{
  "links": [
    "https://s3.amazonaws.com/bucket/bird1.jpg",
    "https://s3.amazonaws.com/bucket/bird2.jpg"
  ]
}
```

## 🎉 **Success Criteria**

Your deployment is successful when:
- ✅ Users can register and verify email
- ✅ Users can login and logout securely
- ✅ Files upload to S3 via presigned URLs
- ✅ Dashboard displays real file data
- ✅ Search by tags returns relevant results
- ✅ Tag updates persist to backend
- ✅ File deletion removes from S3 and database

**Happy Deploying!** 🚀