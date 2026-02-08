"""
Task Manager Lambda Handler
Complete CRUD operations: GET, POST, PUT, DELETE
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
    """Create standardized API response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
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
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        if 'title' not in data:
            return create_response(400, {
                'success': False,
                'error': 'Title is required'
            })
        
        task = {
            'id': str(uuid.uuid4()),
            'title': data['title'],
            'description': data.get('description', ''),
            'status': data.get('status', 'pending'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
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


def update_task(task_id, body):
    """PUT /tasks/{id} - Update a task"""
    try:
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        # Check if task exists
        response = table.get_item(Key={'id': task_id})
        if 'Item' not in response:
            return create_response(404, {
                'success': False,
                'error': f'Task {task_id} not found'
            })
        
        # Build update expression
        update_expr = "SET updated_at = :updated_at"
        expr_values = {':updated_at': datetime.utcnow().isoformat()}
        expr_names = {}
        
        if 'title' in data:
            update_expr += ", title = :title"
            expr_values[':title'] = data['title']
        
        if 'description' in data:
            update_expr += ", description = :description"
            expr_values[':description'] = data['description']
        
        if 'status' in data:
            update_expr += ", #status = :status"
            expr_values[':status'] = data['status']
            expr_names['#status'] = 'status'  # status is reserved word
        
        # Perform update
        update_params = {
            'Key': {'id': task_id},
            'UpdateExpression': update_expr,
            'ExpressionAttributeValues': expr_values,
            'ReturnValues': 'ALL_NEW'
        }
        if expr_names:
            update_params['ExpressionAttributeNames'] = expr_names
        
        result = table.update_item(**update_params)
        
        logger.info(f"Updated task: {task_id}")
        return create_response(200, {
            'success': True,
            'message': 'Task updated successfully',
            'task': result.get('Attributes')
        })
    except json.JSONDecodeError:
        return create_response(400, {
            'success': False,
            'error': 'Invalid JSON in request body'
        })
    except ClientError as e:
        logger.error(f"Error updating task: {e}")
        return create_response(500, {
            'success': False,
            'error': 'Failed to update task'
        })


def delete_task(task_id):
    """DELETE /tasks/{id} - Delete a task"""
    try:
        # Check if task exists
        response = table.get_item(Key={'id': task_id})
        if 'Item' not in response:
            return create_response(404, {
                'success': False,
                'error': f'Task {task_id} not found'
            })
        
        table.delete_item(Key={'id': task_id})
        
        logger.info(f"Deleted task: {task_id}")
        return create_response(200, {
            'success': True,
            'message': f'Task {task_id} deleted successfully'
        })
    except ClientError as e:
        logger.error(f"Error deleting task: {e}")
        return create_response(500, {
            'success': False,
            'error': 'Failed to delete task'
        })


def lambda_handler(event, context):
    """Main Lambda handler - routes requests to CRUD operations"""
    logger.info(f"Event: {json.dumps(event)}")
    
    http_method = event.get('httpMethod', '')
    path_params = event.get('pathParameters') or {}
    task_id = path_params.get('id')
    body = event.get('body', '{}')
    
    # Handle CORS preflight
    if http_method == 'OPTIONS':
        return create_response(200, {'message': 'OK'})
    
    # Route to appropriate handler
    if http_method == 'GET':
        if task_id:
            return get_task(task_id)
        return get_all_tasks()
    
    elif http_method == 'POST':
        return create_task(body)
    
    elif http_method == 'PUT':
        if not task_id:
            return create_response(400, {
                'success': False,
                'error': 'Task ID required for update'
            })
        return update_task(task_id, body)
    
    elif http_method == 'DELETE':
        if not task_id:
            return create_response(400, {
                'success': False,
                'error': 'Task ID required for delete'
            })
        return delete_task(task_id)
    
    return create_response(405, {
        'success': False,
        'error': f'Method {http_method} not allowed'
    })
