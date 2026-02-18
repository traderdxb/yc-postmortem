"""
Vercel Python Handler for Flask App
Vercel Python functions receive a Request and return a Response dict
"""
import json
from app import app

def handler(request):
    """Vercel serverless function handler."""
    # Get request data
    method = request.method
    path = request.url.path
    query = request.url.query
    headers = dict(request.headers)
    body = request.body
    
    # Create a mock WSGI environment
    environ = {
        'REQUEST_METHOD': method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path,
        'QUERY_STRING': query,
        'SERVER_NAME': headers.get('host', 'localhost'),
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'HTTP_HOST': headers.get('host', ''),
        'wsgi.input': None,
        'wsgi.errors': __import__('sys').stderr,
        'wsgi.multithread': True,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add headers to environ
    for key, value in headers.items():
        key = 'HTTP_' + key.upper().replace('-', '_')
        environ[key] = value
    
    # Add body
    if body:
        import io
        environ['wsgi.input'] = io.BytesIO(body)
        environ['CONTENT_LENGTH'] = str(len(body))
    
    # Capture response
    response_status = ['200 OK']
    response_headers = []
    response_body = []
    
    def start_response(status, headers):
        response_status[0] = status
        response_headers.extend(headers)
    
    # Call Flask app
    body_iter = app(environ, start_response)
    for chunk in body_iter:
        response_body.append(chunk)
    body_iter.close()
    
    # Parse status code
    status_code = int(response_status[0].split()[0])
    
    # Build response headers
    headers_out = {}
    for key, value in response_headers:
        headers_out[key.lower()] = value
    
    # Return Vercel response format
    return {
        'statusCode': status_code,
        'headers': headers_out,
        'body': b''.join(response_body).decode('utf-8')
    }
