# AWS Deployment Checklist

## Backend (API Gateway) Configuration

### 1. CORS Configuration
- [ ] Enable CORS for `/files` resource
- [ ] Enable CORS for `/query/by-tags` resource  
- [ ] Enable CORS for `/admin/files/delete` resource
- [ ] Add required headers: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
- [ ] Allow methods: `GET,POST,PUT,DELETE,OPTIONS`
- [ ] Set Access-Control-Allow-Origin to `*` or specific domain

### 2. Deploy API
- [ ] Deploy API to `stage1` stage
- [ ] Test API endpoints with Postman/curl
- [ ] Verify CORS headers in response

## Frontend Deployment

### 1. Build Application
```bash
npm run build
```

### 2. S3 Static Website Hosting
- [ ] Create S3 bucket for static website
- [ ] Upload `dist/` folder contents to S3
- [ ] Enable static website hosting
- [ ] Configure index.html as index document

### 3. CloudFront Distribution (Optional but Recommended)
- [ ] Create CloudFront distribution
- [ ] Point to S3 bucket origin
- [ ] Configure custom error pages for SPA routing
- [ ] Update API Gateway CORS with CloudFront domain

### 4. Domain Configuration (Optional)
- [ ] Configure custom domain in Route 53
- [ ] Update SSL certificate
- [ ] Point domain to CloudFront distribution

## Configuration Updates

### 1. API Endpoint
- [ ] Verify `src/api/axios.js` has correct API Gateway URL
- [ ] Ensure API Gateway URL matches deployment stage

### 2. Cognito Configuration
- [ ] Verify `src/main.js` has correct Cognito User Pool ID
- [ ] Verify App Client ID is correct
- [ ] Update redirect URLs in Cognito if using custom domain

## Testing

### 1. Authentication
- [ ] Test user registration
- [ ] Test email verification
- [ ] Test user login/logout

### 2. File Operations
- [ ] Test file upload
- [ ] Test file listing
- [ ] Test file search
- [ ] Test file deletion

### 3. CORS Verification
- [ ] Open browser dev tools
- [ ] Verify no CORS errors in console
- [ ] Test all API endpoints from deployed frontend

## Troubleshooting

### Common Issues:
1. **CORS Errors**: Check API Gateway CORS configuration
2. **Authentication Failures**: Verify Cognito configuration
3. **File Upload Issues**: Check S3 bucket permissions and presigned URL generation
4. **Route 404s**: Configure CloudFront for SPA routing

### Debug Commands:
```bash
# Test API endpoint directly
curl -X GET "https://oktjqc9h7i.execute-api.ap-southeast-2.amazonaws.com/stage1/files" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Check CORS headers
curl -X OPTIONS "https://oktjqc9h7i.execute-api.ap-southeast-2.amazonaws.com/stage1/files" \
  -H "Origin: https://your-domain.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization"
```
