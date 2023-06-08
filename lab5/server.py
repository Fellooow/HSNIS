# from http.server import BaseHTTPRequestHandler, HTTPServer
# import logging
# import mimetypes
# import os.path
# import parser
#
#
# class S(BaseHTTPRequestHandler):
#     local_path = []
#
#     def _set_response(self):
#         self.send_response(200)
#         self.send_header('Content-type', mimetypes.guess_type(self.path[1::]))
#         self.end_headers()
#
#     def do_GET(self):
#         if self.path != "/favicon.ico":
#             if os.path.exists(self.path[1::]):
#                 self.send_response(200)
#                 self.send_header('Access-Control-Allow-Origin', "http://localhost:" + parser['port'])
#                 self.send_header('Content-type', mimetypes.guess_type(self.path[1::]))
#                 self.end_headers()
#                 self.log_message('"%s" %s ',self.requestline, str(200))
#                 logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
#                 self.local_path.append(self.path[1::])
#                 with open(self.local_path[0], "rb") as data:
#                     f = data.read()
#                     b = bytearray(f)
#                     self.wfile.write(b)
#                 self.local_path.pop()
#                 with open("request.log", "a") as file:
#                     log = "GET request /HTTP/1.1 200\nPath:\n{} \nHeaders:\n{}\n".format(self.path[1::],
#                                                                                          self.headers)
#                     file.write(log)
#             else:
#                 self.send_response(500)
#                 # self.send_header('Content-type', mimetypes.guess_type(self.path[1::]))
#                 self.end_headers()
#                 with open("request.log", "a") as file:
#                     log = "GET request /HTTP/1.1 200\nPath:\n{} \nHeaders:\n{}\n".format(self.path[1::],
#                                                                                          self.headers)
#                     file.write(log)
#
#     def do_POST(self):
#         if os.path.exists(self.path[1::]):
#             self.send_response(200)
#             self.send_header('Access-Control-Allow-Origin', "http://localhost:" + argument_parser['port'])
#             self.send_header('Content-type', mimetypes.guess_type(self.path[1::]))
#             self.end_headers()
#             with open(self.path[1::], "rb") as file:
#                 data = file.read()
#             b = bytearray(data)
#             with open("files/post/" + self.path[1::], 'wb') as file:
#                 file.write(b)
#             with open("request.log", "a") as file:
#                 log = "POST request /HTTP/1.1 200\nPath:\n{} \nHeaders:\n{}\n".format(self.path[1::], self.headers)
#                 file.write(log)
#         else:
#             self.send_response(400)
#             # self.send_header('Content-type', mimetypes.guess_type(self.path[1::]))
#             self.end_headers()
#             with open("request.log", "a") as file:
#                 log = "POST request /HTTP/1.1 400\nPath:\n{} \nHeaders:\n{}\n".format(self.path[1::], self.headers)
#                 file.write(log)
#
#     def do_OPTIONS(self):
#         self.send_response(200)
#         self.send_header('Access-Control-Allow-Origin', "http://localhost:" + argument_parser['port'])
#         self.send_header('Access-Control-Allow-Methods', "POST, GET, OPTIONS")
#         self.end_headers()
#         with open("request.log", "a") as file:
#             log = "OPTIONS request /HTTP/1.1 200 \nHeaders:\n{}\n".format(self.headers)
#             file.write(log)
#
#
# def run(server_class=HTTPServer, handler_class=S, port=8080):
#     logging.basicConfig(level=logging.INFO)
#
#     server_address = ('', port)
#     httpd = server_class(server_address, handler_class)
#     logging.info('Starting httpd...\n')
#     try:
#         httpd.serve_forever()
#     except KeyboardInterrupt:
#         pass
#     httpd.server_close()
#     logging.info('Stopping httpd...\n')
#
#
# if __name__ == '__main__':
#     argument_parser = parser.parse_arguments()
#     run(port=argument_parser['port'])


import os.path
import http.server
from http.server import BaseHTTPRequestHandler
import socketserver
import argparse
from logger import Logger

parser = argparse.ArgumentParser(description='HTTP 1.1 server')
parser.add_argument('port', type=int, help='port to connections')
parser.add_argument("-o", "--origin",
                    help="Access-Control-Allow-Origin default header",
                    action="store_true")
parser.add_argument("-m", "--methods",
                    help="Access-Control-Allow-Methods default header",
                    action="store_true")

logger = Logger('.log')

args = parser.parse_args()

PORT = args.port
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def handle_errors(foo):
    def inner(*args, **kwargs):
        try:
            foo(*args, **kwargs)
        except Exception as e:
            logger.log_error(str(e))

    return inner


class Handler(BaseHTTPRequestHandler):
    @handle_errors
    def do_GET(self):
        request_path = os.path.join(BASE_DIR, self.path[1:])
        print(request_path, self.path, BASE_DIR)
        if os.path.isfile(request_path):
            self.send_response(200, 'ok')
            self.end_headers()
            with open(request_path, 'rb') as file:
                content = file.read()
                self.wfile.write(content)
            logger.log_response(
                'GET',
                str(404),
                str(self.headers),
                str(self.path),
                str(content)
            )
        else:
            self.send_response(404)
            self.end_headers()
            logger.log_response(
                'GET',
                str(404),
                str(self.headers),
                str(self.path),
                ''
            )

    @handle_errors
    def do_POST(self):
        try:
            self.send_response(200, 'ok')
            length = int(self.headers.get('content-length'))
            body = self.rfile.read(length)
            logger.log_response(
                'POST',
                str(200),
                str(self.headers),
                str(self.path),
                str(body)
            )
        except:
            self.send_response(500)

    @handle_errors
    def do_OPTIONS(self):
        self.send_response(200, 'ok')

        headers = []
        if args.origin:
            self.send_header(
                'Access-Control-Allow-Origin',
                'http://localhost:' + str(PORT)
            )
            headers.append({'Access-Control-Allow-Origin': 'http://localhost:' + str(PORT)})

        if args.methods:
            self.send_header(
                'Access-Control-Allow-Methods',
                'GET, POST, OPTIONS'
            )
            headers.append({'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'})

        self.end_headers()

        logger.log_response(
            'OPTIONS',
            str(200),
            str(headers),
            str(self.path),
            ''
        )


class Server:
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/tmp/foo.pid'
        self.pidfile_timeout = 5

    def run(self):
        try:
            with socketserver.TCPServer(('', PORT), Handler) as httpd:
                print("Serving at port", PORT)
                logger.log_start(PORT)
                httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            print('\nServer shutted down')
            logger.log_shutdown()


if __name__ == "__main__":
    Server().run()