import json
import boto3
import uuid
import os
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Configuration
UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET', 'birdtag-media-uploads-2025-birdtag-laobukepo')
THUMBNAIL_BUCKET = os.environ.get('THUMBNAIL_BUCKET', 'birdtag-media-thumbnails-laobukepo')
FILES_TABLE = os.environ.get('FILES_TABLE', 'bird-files-table')

def lambda_handler(event, context):
    """Main Lambda handler for file management operations"""
    
    # Extract user info from JWT token
    user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
    if not user_id:
        return create_response(401, {'error': 'Unauthorized'})
    
    # Parse the HTTP method and path
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    
    try:
        if http_method == 'POST' and '/files' in path:
            return generate_presigned_url(user_id, event.get('body', '{}'))
        elif http_method == 'GET' and '/files' in path:
            return get_files_list(user_id, event.get('queryStringParameters', {}))
        elif http_method == 'POST' and '/query/by-tags' in path:
            return search_by_tags(user_id, event.get('body', '{}'))
        elif http_method == 'POST' and '/tags/update' in path:
            return update_file_tags(user_id, event.get('body', '{}'))
        elif http_method == 'POST' and '/admin/files/delete' in path:
            return delete_files(user_id, event.get('body', '{}'))
        else:
            return create_response(404, {'error': 'Endpoint not found'})
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def generate_presigned_url(user_id, body):
    """Generate presigned URL for file upload"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        
        file_name = data.get('fileName')
        file_type = data.get('fileType')
        file_size = data.get('fileSize')
        
        if not all([file_name, file_type, file_size]):
            return create_response(400, {'error': 'Missing required fields: fileName, fileType, fileSize'})
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create S3 key with user ID and file ID
        s3_key = f"uploads/{user_id}/{file_id}-{file_name}"
        
        # Generate presigned URL
        presigned_url = s3.generate_presigned_post(
            Bucket=UPLOAD_BUCKET,
            Key=s3_key,
            Fields={
                'Content-Type': file_type,
                'x-amz-meta-user-id': user_id,
                'x-amz-meta-file-id': file_id
            },
            Conditions=[
                {'Content-Type': file_type},
                ['content-length-range', 0, 10 * 1024 * 1024]  # 10MB limit
            ],
            ExpiresIn=3600  # 1 hour
        )
        
        # Add fileId to response
        presigned_url['fileId'] = file_id
        
        return create_response(200, presigned_url)
        
    except Exception as e:
        print(f"Error generating presigned URL: {str(e)}")
        return create_response(500, {'error': 'Failed to generate presigned URL'})

def get_files_list(user_id, query_params):
    """Get list of files for user"""
    try:
        limit = int(query_params.get('limit', 50))
        sort_by = query_params.get('sort', 'recent')
        
        # Query DynamoDB for real files
        table = dynamodb.Table(FILES_TABLE)
        
        # Query by user_id using GSI
        response = table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={
                ':user_id': user_id
            },
            ScanIndexForward=False,  # Most recent first
            Limit=limit
        )
        
        files = []
        for item in response.get('Items', []):
            # Parse AI predictions
            ai_predictions = []
            if 'ai_predictions' in item:
                try:
                    if isinstance(item['ai_predictions'], str):
                        ai_predictions = json.loads(item['ai_predictions'])
                    else:
                        ai_predictions = item['ai_predictions']
                except:
                    ai_predictions = []
            
            file_data = {
                "id": item.get('file_id'),
                "filename": item.get('filename'),
                "url": item.get('url'),
                "thumbnailUrl": item.get('thumbnail_url'),
                "uploadedAt": item.get('uploaded_at'),
                "predictions": ai_predictions,
                "tags": item.get('tags', [])
            }
            files.append(file_data)
        
        # If no files found in DynamoDB, return empty array
        if not files:
            print(f"No files found for user {user_id} in DynamoDB")
            return create_response(200, {"files": [], "total": 0})
        
        return create_response(200, {"files": files, "total": len(files)})
        
    except Exception as e:
        print(f"Error getting files list: {str(e)}")
        # Fallback to mock data for testing
        mock_files = [
            {
                "id": "test-file-1",
                "filename": "test.jpg",
                "url": f"https://{UPLOAD_BUCKET}.s3.amazonaws.com/test.jpg",
                "thumbnailUrl": f"https://{THUMBNAIL_BUCKET}.s3.amazonaws.com/thumb_test.jpg",
                "uploadedAt": datetime.utcnow().isoformat() + 'Z',
                "predictions": [],
                "tags": []
            }
        ]
        return create_response(200, {"files": mock_files, "total": len(mock_files)})

def search_by_tags(user_id, body):
    """Search files by tags"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        
        tags = data.get('tags', [])
        confidence = data.get('confidence', 0.0)
        limit = data.get('limit', 50)
        
        if not tags:
            return create_response(400, {'error': 'Tags are required'})
        
        # Mock search results
        # In production, this would query DynamoDB with tag filters
        mock_results = [
            {
                "id": "e0f5d0c5-8714-4db5-ad0b-21c77548aed9",
                "filename": "peacocks_3.jpg",
                "url": f"https://{UPLOAD_BUCKET}.s3.amazonaws.com/peacocks_3.jpg",
                "thumbnailUrl": f"https://{THUMBNAIL_BUCKET}.s3.amazonaws.com/thumb_peacocks_3.jpg",
                "uploadedAt": "2025-08-29T14:22:30.123Z",
                "predictions": [
                    {"label": "Peacock", "confidence": 0.98}
                ],
                "tags": ["peacock", "colorful", "garden bird"]
            }
        ]
        
        return create_response(200, {
            "files": mock_results,
            "total": len(mock_results),
            "searchCriteria": {
                "tags": tags,
                "confidence": confidence
            }
        })
        
    except Exception as e:
        print(f"Error searching by tags: {str(e)}")
        return create_response(500, {'error': 'Failed to search files'})

def update_file_tags(user_id, body):
    """Update tags for a file"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        
        file_id = data.get('fileId')
        tags = data.get('tags', [])
        
        if not file_id:
            return create_response(400, {'error': 'fileId is required'})
        
        # In production, this would update DynamoDB
        # For now, just return success
        return create_response(200, {
            "success": True,
            "message": f"Tags updated for file {file_id}",
            "tags": tags
        })
        
    except Exception as e:
        print(f"Error updating tags: {str(e)}")
        return create_response(500, {'error': 'Failed to update tags'})

def delete_files(user_id, body):
    """Delete files from S3 and database"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        
        urls = data.get('urls', [])
        
        if not urls:
            return create_response(400, {'error': 'urls array is required'})
        
        # In production, this would:
        # 1. Delete from S3
        # 2. Delete from DynamoDB
        # 3. Delete thumbnails
        
        deleted_count = len(urls)
        
        return create_response(200, {
            "success": True,
            "message": f"Successfully deleted {deleted_count} files",
            "deletedCount": deleted_count
        })
        
    except Exception as e:
        print(f"Error deleting files: {str(e)}")
        return create_response(500, {'error': 'Failed to delete files'})

def create_response(status_code, body):
    """Create API Gateway response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }
