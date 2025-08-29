# Backend Deployment Guide

This guide will help you deploy the backend Lambda functions to fix the "Recent Uploads" issue.

## 🎯 **Problem Summary**

The issue is that your backend API is returning **hardcoded test data** instead of real file records. This happens because:

1. **Missing Lambda Functions**: Only notification functions exist, no file management functions
2. **No S3 Triggers**: Files uploaded to S3 are not being processed
3. **No Database**: No DynamoDB table to store file metadata

## 🛠️ **Solution: Deploy Backend Infrastructure**

### Step 1: Prepare Lambda Function Code

1. **Create deployment packages** for the Lambda functions:

```bash
cd FIT5225/backend

# Create deployment directory
mkdir -p deployment

# Copy Lambda function code
cp file_management_lambda.py deployment/
cp s3_processor_lambda.py deployment/

# Create ZIP files (if needed for manual deployment)
cd deployment
zip -r file-management.zip file_management_lambda.py
zip -r s3-processor.zip s3_processor_lambda.py
```

### Step 2: Deploy Using CloudFormation

```bash
# Deploy the backend infrastructure
aws cloudformation deploy \
  --template-file cloudformation-backend.yaml \
  --stack-name bird-recognition-backend \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    UserPoolId=ap-southeast-2_xMyeYNwU4 \
    UserPoolClientId=41f6f90eaa49b08hm4fp9u2s6o \
    UploadBucket=birdtag-media-uploads-2025-birdtag-laobukepo \
    ThumbnailBucket=birdtag-media-thumbnails-laobukepo
```

### Step 3: Update Lambda Function Code

After CloudFormation creates the Lambda functions, you need to update them with the actual code:

#### Option A: Using AWS CLI
```bash
# Update file management function
aws lambda update-function-code \
  --function-name bird-file-management \
  --zip-file file://deployment/file-management.zip

# Update S3 processor function  
aws lambda update-function-code \
  --function-name bird-s3-processor \
  --zip-file file://deployment/s3-processor.zip
```

#### Option B: Using AWS Console
1. Go to AWS Lambda Console
2. Find the `bird-file-management` function
3. Click "Code" tab
4. Replace the placeholder code with the content from `file_management_lambda.py`
5. Repeat for `bird-s3-processor` function

### Step 4: Configure S3 Event Notifications

The CloudFormation template should automatically configure S3 event notifications, but verify:

1. Go to S3 Console
2. Select your upload bucket: `birdtag-media-uploads-2025-birdtag-laobukepo`
3. Go to "Properties" → "Event notifications"
4. Verify there's a notification for `s3:ObjectCreated:*` events
5. It should trigger the `bird-s3-processor` Lambda function

### Step 5: Test the Backend

#### Test Presigned URL Generation
```bash
# Test with curl (replace with your actual API Gateway URL)
curl -X POST "https://oktjqc9h7i.execute-api.ap-southeast-2.amazonaws.com/stage1/files" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "fileName": "test.jpg",
    "fileType": "image/jpeg", 
    "fileSize": 1024000
  }'
```

Expected response:
```json
{
  "url": "https://s3.amazonaws.com/...",
  "fields": {
    "key": "uploads/user123/uuid-test.jpg",
    "policy": "...",
    "signature": "..."
  },
  "fileId": "uuid-generated-id"
}
```

#### Test File Listing
```bash
curl -X GET "https://oktjqc9h7i.execute-api.ap-southeast-2.amazonaws.com/stage1/files?limit=6&sort=recent" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔧 **Manual Configuration (Alternative)**

If CloudFormation deployment fails, you can manually create the resources:

### 1. Create DynamoDB Table
```bash
aws dynamodb create-table \
  --table-name bird-files-table \
  --attribute-definitions \
    AttributeName=file_id,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
    AttributeName=uploaded_at,AttributeType=S \
  --key-schema AttributeName=file_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    IndexName=UserIdIndex,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=uploaded_at,KeyType=RANGE}],Projection={ProjectionType=ALL}
```

### 2. Create IAM Role
```bash
# Create trust policy
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name BirdRecognitionLambdaRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name BirdRecognitionLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### 3. Create Lambda Functions
```bash
# Create file management function
aws lambda create-function \
  --function-name bird-file-management \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/BirdRecognitionLambdaRole \
  --handler file_management_lambda.lambda_handler \
  --zip-file file://deployment/file-management.zip \
  --timeout 30 \
  --memory-size 256

# Create S3 processor function
aws lambda create-function \
  --function-name bird-s3-processor \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/BirdRecognitionLambdaRole \
  --handler s3_processor_lambda.lambda_handler \
  --zip-file file://deployment/s3-processor.zip \
  --timeout 60 \
  --memory-size 512
```

## 🧪 **Testing After Deployment**

### 1. Upload a New Image
1. Go to your frontend application
2. Upload a new image
3. Check the console for:
   - `File ID from presigned response:` - Should show a UUID
   - `Extracted fileId from S3 key:` - Should show the same UUID

### 2. Check Recent Uploads
1. After upload, wait 5-10 seconds
2. Click "Refresh" on Recent Uploads
3. The new file should appear in the list

### 3. Check CloudWatch Logs
1. Go to AWS CloudWatch Console
2. Check logs for `bird-file-management` and `bird-s3-processor` functions
3. Look for any errors or processing logs

## 🚨 **Troubleshooting**

### Common Issues:

1. **Lambda Function Not Found**
   - Verify the function names match exactly
   - Check the AWS region

2. **Permission Denied**
   - Verify IAM role has correct permissions
   - Check S3 bucket permissions

3. **S3 Event Not Triggering**
   - Verify event notification is configured
   - Check Lambda function permissions for S3 invocation

4. **CORS Errors**
   - Verify API Gateway CORS settings
   - Check Lambda response headers

### Debug Commands:
```bash
# Check Lambda function status
aws lambda get-function --function-name bird-file-management

# Check S3 event notifications
aws s3api get-bucket-notification-configuration \
  --bucket birdtag-media-uploads-2025-birdtag-laobukepo

# Test Lambda function directly
aws lambda invoke \
  --function-name bird-file-management \
  --payload '{"httpMethod":"GET","path":"/files"}' \
  response.json
```

## ✅ **Success Criteria**

After deployment, you should see:

1. **Presigned URLs with fileId**: `"fileId": "uuid-generated-id"`
2. **Real file data**: Recent Uploads shows actual uploaded files
3. **S3 processing**: CloudWatch logs show file processing
4. **No more hardcoded data**: API returns real database records

## 📋 **Next Steps**

Once the backend is deployed:

1. **Test file upload and listing**
2. **Verify S3 triggers work**
3. **Check DynamoDB for file records**
4. **Monitor CloudWatch logs for errors**

The "Recent Uploads" should now show your newly uploaded files instead of hardcoded test data!
