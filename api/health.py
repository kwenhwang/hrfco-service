import json
from datetime import datetime

def handler(event, context):
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'hrfco-mcp-netlify',
            'version': '1.0.0'
        })
    }
