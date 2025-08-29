import json
import boto3
import os
import uuid
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
    """Process files uploaded to S3"""
    try:
        for record in event.get('Records', []):
            if record.get('eventSource') == 'aws:s3':
                bucket_name = record['s3']['bucket']['name']
                object_key = record['s3']['object']['key']
                
                print(f"Processing file: {object_key} from bucket: {bucket_name}")
                
                # Extract file information from S3 key
                file_info = extract_file_info(object_key)
                
                # Process the file
                process_uploaded_file(bucket_name, object_key, file_info)
        
        return {'statusCode': 200, 'body': 'Files processed successfully'}
        
    except Exception as e:
        print(f"Error processing S3 event: {str(e)}")
        return {'statusCode': 500, 'body': 'Error processing files'}

def extract_file_info(s3_key):
    """Extract file information from S3 key"""
    try:
        # Expected format: uploads/{user_id}/{file_id}-{filename}
        parts = s3_key.split('/')
        if len(parts) >= 3:
            user_id = parts[1]
            file_id_filename = parts[2]
            
            # Split file_id and filename
            if '-' in file_id_filename:
                file_id, filename = file_id_filename.split('-', 1)
            else:
                file_id = str(uuid.uuid4())
                filename = file_id_filename
            
            return {
                'user_id': user_id,
                'file_id': file_id,
                'filename': filename,
                's3_key': s3_key
            }
        else:
            # Fallback for different key formats
            return {
                'user_id': 'unknown',
                'file_id': str(uuid.uuid4()),
                'filename': s3_key.split('/')[-1],
                's3_key': s3_key
            }
    except Exception as e:
        print(f"Error extracting file info: {str(e)}")
        return {
            'user_id': 'unknown',
            'file_id': str(uuid.uuid4()),
            'filename': s3_key.split('/')[-1],
            's3_key': s3_key
        }

def process_uploaded_file(bucket_name, object_key, file_info):
    """Process an uploaded file"""
    try:
        print(f"Processing file: {file_info['filename']} for user: {file_info['user_id']}")
        
        # Generate thumbnail (simplified - in production, use image processing)
        thumbnail_url = generate_thumbnail(bucket_name, object_key, file_info)
        
        # Perform AI recognition (simplified - in production, call AI service)
        ai_predictions = perform_ai_recognition(bucket_name, object_key, file_info)
        
        # Store file metadata in database
        store_file_metadata(file_info, thumbnail_url, ai_predictions)
        
        print(f"Successfully processed file: {file_info['filename']}")
        
    except Exception as e:
        print(f"Error processing file {file_info['filename']}: {str(e)}")

def generate_thumbnail(bucket_name, object_key, file_info):
    """Generate thumbnail for the uploaded image"""
    try:
        # In production, this would:
        # 1. Download the image from S3
        # 2. Resize it using PIL or similar
        # 3. Upload thumbnail to thumbnail bucket
        
        # For now, return a mock thumbnail URL
        thumbnail_key = f"thumb_{file_info['filename']}"
        thumbnail_url = f"https://{THUMBNAIL_BUCKET}.s3.amazonaws.com/{thumbnail_key}"
        
        print(f"Generated thumbnail URL: {thumbnail_url}")
        return thumbnail_url
        
    except Exception as e:
        print(f"Error generating thumbnail: {str(e)}")
        return None

def perform_ai_recognition(bucket_name, object_key, file_info):
    """Perform AI recognition on the uploaded image"""
    try:
        # In production, this would:
        # 1. Call AWS Rekognition or similar AI service
        # 2. Process the results
        # 3. Return structured predictions
        
        # For now, return mock AI predictions
        mock_predictions = [
            {
                "label": "Bird",
                "confidence": 0.95,
                "description": "A beautiful bird in natural habitat"
            }
        ]
        
        # Add some variety based on filename
        if "peacock" in file_info['filename'].lower():
            mock_predictions = [
                {
                    "label": "Peacock",
                    "confidence": 0.98,
                    "description": "A magnificent peacock with colorful plumage"
                }
            ]
        elif "sparrow" in file_info['filename'].lower():
            mock_predictions = [
                {
                    "label": "House Sparrow",
                    "confidence": 0.85,
                    "description": "A small house sparrow in urban setting"
                }
            ]
        
        print(f"AI predictions: {mock_predictions}")
        return mock_predictions
        
    except Exception as e:
        print(f"Error performing AI recognition: {str(e)}")
        return []

def store_file_metadata(file_info, thumbnail_url, ai_predictions):
    """Store file metadata in DynamoDB"""
    try:
        metadata = {
            'file_id': file_info['file_id'],
            'user_id': file_info['user_id'],
            'filename': file_info['filename'],
            's3_key': file_info['s3_key'],
            'url': f"https://{UPLOAD_BUCKET}.s3.amazonaws.com/{file_info['s3_key']}",
            'thumbnail_url': thumbnail_url,
            'ai_predictions': ai_predictions,
            'uploaded_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'processed'
        }
        
        print(f"Storing file metadata in DynamoDB: {json.dumps(metadata, indent=2)}")
        
        # Store in DynamoDB
        table = dynamodb.Table(FILES_TABLE)
        table.put_item(Item=metadata)
        
        print(f"Successfully stored metadata for file {file_info['filename']} in DynamoDB")
        
    except Exception as e:
        print(f"Error storing file metadata: {str(e)}")
        raise e
