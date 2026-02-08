"""
Task Manager Lambda Handler
Implementing GET and POST endpoints
"""

import json
import os
import uuid
import logging
from datetime import datetime
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'tasks')
table = dynamodb.Table(table_name)


class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal types from DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def create_response(status_code, body):
    """Create standardized API response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }


def get_all_tasks():
    """GET /tasks - List all tasks"""
    try:
        response = table.scan()
        tasks = response.get('Items', [])
        
        logger.info(f"Retrieved {len(tasks)} tasks")
        return create_response(200, {
            'success': True,
            'count': len(tasks),
            'tasks': tasks
        })
    except ClientError as e:
        logger.error(f"Error getting tasks: {e}")
        return create_response(500, {
            'success': False,
            'error': 'Failed to retrieve tasks'
        })


def get_task(task_id):
    """GET /tasks/{id} - Get single task"""
    try:
        response = table.get_item(Key={'id': task_id})
        task = response.get('Item')
        
        if not task:
            return create_response(404, {
                'success': False,
                'error': f'Task {task_id} not found'
            })
        
        return create_response(200, {
            'success': True,
            'task': task
        })
    except ClientError as e:
        logger.error(f"Error getting task: {e}")
        return create_response(500, {
            'success': False,
            'error': 'Failed to retrieve task'
        })


def create_task(body):
    """POST /tasks - Create a new task"""
    try:
        # Parse request body
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        # Validate required fields
        if 'title' not in data:
            return create_response(400, {
                'success': False,
                'error': 'Title is required'
            })
        
        # Create task item
        task = {
            'id': str(uuid.uuid4()),
            'title': data['title'],
            'description': data.get('description', ''),
            'status': data.get('status', 'pending'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Save to DynamoDB
        table.put_item(Item=task)
        
        logger.info(f"Created task: {task['id']}")
        return create_response(201, {
            'success': True,
            'message': 'Task created successfully',
            'task': task
        })
    except json.JSONDecodeError:
        return create_response(400, {
            'success': False,
            'error': 'Invalid JSON in request body'
        })
    except ClientError as e:
        logger.error(f"Error creating task: {e}")
        return create_response(500, {
            'success': False,
            'error': 'Failed to create task'
        })


def lambda_handler(event, context):
    """Main Lambda handler"""
    logger.info(f"Event: {json.dumps(event)}")
    
    http_method = event.get('httpMethod', '')
    path_params = event.get('pathParameters') or {}
    task_id = path_params.get('id')
    body = event.get('body', '{}')
    
    # Route to appropriate handler
    if http_method == 'GET':
        if task_id:
            return get_task(task_id)
        return get_all_tasks()
    
    elif http_method == 'POST':
        return create_task(body)
    
    return create_response(405, {
        'success': False,
        'error': f'Method {http_method} not allowed'
    })
