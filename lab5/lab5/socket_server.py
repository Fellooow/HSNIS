import socket
import json
import os
from urllib.parse import urlparse, parse_qs

class HTTPServer:
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
        self.routes = {}

    def add_route(self, method, path):
        def decorator(handler):
            self.routes[method.upper(), path] = handler
            return handler
        return decorator

    def handle_request(self, client_socket):
        try:
            request_data = client_socket.recv(1024).decode()
            method, path, version = request_data.split(' ')[0:3]
            headers = request_data.split('\r\n')[1:-2]
            body = request_data.split('\r\n')[-1]

            handler = self.routes.get((method.upper(), path))
            if not handler:
                if os.path.isfile(BASE_DIR + '\\' + path):
                    handler = self.routes.get((method.upper(), '/file'))
                else:
                    handler = self.routes.get((method.upper(), '/file'))
            if handler:
                request = {
                    'method': method,
                    'path': path,
                    'headers': headers,
                    'body': body
                }
                response = handler(request)
            else:
                response = self.make_response(404, {'message': 'Not Found'})

        except Exception as ex:
            response = self.make_response(404, {'message': 'Not Found'})

        client_socket.send(response.encode())
        client_socket.close()

    def make_response(self, status_code, data: dict):
        status_text = self.get_status_text(status_code)
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': str(10 * 1024 * 1024),
            'maximumContentLength ': ''
        }
        headers['Content-Length'] = len(json.dumps(data, indent=2))

        response = f'HTTP/1.1 {status_code} {status_text}\r\n'
        for name, value in headers.items():
            response += f'{name}: {value}\r\n'
        response += '\r\n'
        response += json.dumps(data, indent=2) + "\n\r\n\n"
        return response

    def get_status_text(self, status_code):
        texts = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            400: 'Bad Request',
            404: 'Not Found',
            405: 'Method Not Allowed',
            500: 'Internal Server Error'
        }
        return texts.get(status_code, 'Unknown')

    def get_http_date(self):
        import time
        return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())

    def serve_forever(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((self.host, self.port))
                server_socket.listen(1)
                print(f'Server listening on {self.host}:{self.port}...')
                while True:
                    client_socket, address = server_socket.accept()
                    print(f'Connection from {address}')
                    self.handle_request(client_socket)
        except KeyboardInterrupt:
            server_socket.shutdown(1)
            print('\nServer shutted down')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
server = HTTPServer()

@server.add_route('GET', '/file')
def handle_get_request(request):
    url = urlparse(request['path'])
    print(url.path)
    print(BASE_DIR)
    print(BASE_DIR+'\\'+url.path[1:])
    content = ""
    if os.path.isfile(BASE_DIR+'\\'+url.path[1:]):
      with open(BASE_DIR+url.path, 'r') as file:
        content = file.read()
    params = parse_qs(url.query)
    response = {'message': 'GET Request Received', 'params': params,'body': content}
    return server.make_response(200, response)

@server.add_route('POST', '/file')
def handle_post_request(request):
    url = urlparse(request['path'])
    content = ""
    code = 500
    print(request['body'])
    try:
        # if os.path.isfile(BASE_DIR+'\\'+url.path[1:]):
        with open(BASE_DIR + url.path, "w") as file:
            content = file.write(request["body"])
        code = 200
    except Exception as ex:
        content = ex
    params = parse_qs(url.query)
    response = {"message": "POST Request Received", "params": params, "body": content}
    return server.make_response(code, response)

@server.add_route('GET', '/')
def handle_get_request(request):
    response = {'message': 'Not Found'}
    return server.make_response(404, response)

"""@server.add_route('POST', '/')
def handle_post_request(request):
    content_length = int(request['headers'][0].split('Content-Length: ')[-1])
    data = json.loads(request['body'])
    response = {'message': 'POST Request Received', 'data': data}
    return server.make_response(200, response)"""

@server.add_route('OPTIONS', '/')
def handle_options_request(request):
    data = {"available requests": ["GET", "POST", "OPTIONS"]}
    response = {'message': 'OPTIONS Request Received', 'data': data}
    return server.make_response(200,  response)



server.serve_forever()
