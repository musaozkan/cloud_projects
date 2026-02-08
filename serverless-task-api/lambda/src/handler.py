"""
Task Manager Lambda Handler
Placeholder - will implement CRUD operations
"""

import json


def lambda_handler(event, context):
    """Main Lambda handler - placeholder for now"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Hello from Lambda!',
            'status': 'placeholder'
        })
    }
