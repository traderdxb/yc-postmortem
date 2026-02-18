import os
import sys

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the Flask app
from app import app

# Vercel handler function
def handler(request):
    """Vercel Python handler function."""
    return app(request.environ, lambda status, headers: 
        VercelResponse(status, headers))

class VercelResponse:
    def __init__(self, status, headers):
        self.status = status
        self.headers = headers
    
    def __call__(self, body):
        return {
            'statusCode': int(self.status.split()[0]),
            'headers': dict(self.headers),
            'body': body
        }
