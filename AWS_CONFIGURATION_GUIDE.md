# AWS Configuration Guide

This guide will help you configure AWS services for the Bird Recognition System.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Node.js and npm installed

## Current AWS Resources

Based on your AWS console, you have the following resources:

### Cognito User Pool
- **Name**: `birdtag-user-pool`
- **ID**: `ap-southeast-2_xMyeYNwU4`
- **Region**: `ap-southeast-2` (Asia Pacific - Sydney)
- **App Client Name**: `birdtag-webapp-client`
- **App Client ID**: `41f6f90eaa49b08hm4fp9u2s6o`

### API Gateway
- **Name**: `BirdTag-API`
- **ID**: `oktjqc9h7i`
- **URL**: `https://oktjqc9h7i.execute-api.ap-southeast-2.amazonaws.com/stage1`

### S3 Buckets
- **Main Upload Bucket**: `birdtag-media-uploads-2025-birdtag-laobukepo`
- **Thumbnails Bucket**: `birdtag-media-thumbnails-laobukepo`
- **Deployment Assets**: `birdtag-deployment-assets`

## Configuration Steps

### Step 1: Get Cognito App Client ID

1. **Login to AWS Console**
2. **Navigate to Amazon Cognito**
3. **Select your User Pool**: `birdtag-user-pool`
4. **Click "App integration" tab**
5. **Scroll to "App clients and analytics"**
6. **Copy the App Client ID**

### Step 2: Update Frontend Configuration

Edit `src/aws-exports.js` and replace `YOUR_APP_CLIENT_ID` with the actual App Client ID:

```javascript
const awsconfig = {
  Auth: {
    region: 'ap-southeast-2',
    userPoolId: 'ap-southeast-2_xMyeYNwU4',
    userPoolWebClientId: '41f6f90eaa49b08hm4fp9u2s6o', // Your actual App Client ID
    mandatorySignIn: true,
    authenticationFlowType: 'USER_SRP_AUTH'
  },
  // ... rest of config
}
```

### Step 3: Configure API Gateway Endpoints

Ensure your API Gateway has the following endpoints:

#### Required Endpoints
- `POST /files` - Generate presigned URLs
- `GET /files` - Get file list
- `POST /query/by-tags` - Search by tags
- `POST /tags/update` - Update file tags
- `POST /admin/files/delete` - Delete files

#### Optional Notification Endpoints
- `GET /notifications/subscriptions` - Get user subscriptions
- `POST /notifications/subscribe` - Subscribe to tags
- `POST /notifications/unsubscribe` - Unsubscribe from tags
- `POST /notifications/preferences` - Update preferences

### Step 4: Configure S3 Bucket CORS

Add CORS configuration to your S3 bucket:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
    "AllowedOrigins": ["http://localhost:5173", "https://your-domain.com"],
    "ExposeHeaders": ["ETag"]
  }
]
```

### Step 5: Set Up Lambda Functions

Create Lambda functions for your backend logic:

#### Required Lambda Functions
1. **File Upload Handler** - Generate presigned URLs
2. **File Processing** - Handle S3 uploads and AI processing
3. **File Management** - CRUD operations for files
4. **Search Handler** - Tag-based search functionality

#### Optional Lambda Functions
1. **Notification Management** - Handle subscriptions
2. **Notification Sender** - Send email notifications

### Step 6: Configure IAM Roles

Ensure Lambda functions have appropriate IAM roles with permissions for:
- S3 access
- DynamoDB access
- SES (for notifications)
- Cognito access

## Testing Configuration

### 1. Test Authentication
```bash
# Start the development server
npm run dev

# Try to register/login a user
# Check browser console for any authentication errors
```

### 2. Test File Upload
```bash
# Upload a test image
# Check if presigned URL generation works
# Verify file appears in S3 bucket
```

### 3. Test API Endpoints
```bash
# Test API endpoints using curl or Postman
curl -X GET https://oktjqc9h7i.execute-api.ap-southeast-2.amazonaws.com/stage1/files \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check S3 bucket CORS configuration
   - Verify API Gateway CORS settings

2. **Authentication Errors**
   - Verify Cognito User Pool ID
   - Check App Client ID
   - Ensure user is confirmed in Cognito

3. **API Gateway Errors**
   - Check Lambda function permissions
   - Verify API Gateway integration
   - Check CloudWatch logs

4. **S3 Upload Errors**
   - Verify bucket permissions
   - Check presigned URL generation
   - Ensure bucket exists and is accessible

### Debug Steps

1. **Check Browser Console** for JavaScript errors
2. **Check Network Tab** for failed API calls
3. **Check CloudWatch Logs** for Lambda function errors
4. **Verify AWS Credentials** are properly configured

## Security Considerations

1. **Environment Variables** - Don't commit sensitive data to version control
2. **IAM Permissions** - Use least privilege principle
3. **CORS Configuration** - Restrict allowed origins in production
4. **API Gateway** - Enable authentication for all endpoints
5. **S3 Bucket** - Configure appropriate access policies

## Production Deployment

For production deployment:

1. **Update CORS origins** to your production domain
2. **Configure custom domain** for API Gateway
3. **Set up CloudFront** for S3 bucket
4. **Enable CloudWatch monitoring**
5. **Set up error tracking** (e.g., Sentry)
6. **Configure SSL certificates**

## Cost Optimization

1. **S3 Lifecycle Policies** - Archive old files
2. **Lambda Timeout** - Optimize function execution time
3. **API Gateway Caching** - Enable caching for frequently accessed data
4. **CloudWatch Logs** - Set up log retention policies
5. **DynamoDB** - Use on-demand billing for low traffic

## Support

If you encounter issues:

1. **Check AWS Documentation** for specific services
2. **Review CloudWatch Logs** for detailed error information
3. **Test with AWS CLI** to isolate issues
4. **Contact AWS Support** if needed
