import os.path
import logging
from time import gmtime, strftime


class Logger:
    def __init__(self, filename):
        self.port = 0
        if not os.path.exists(filename):
            open(filename, "w")
        logging.basicConfig(
            filename=filename,
            level=logging.DEBUG,
            format='%(asctime)s %(message)s'
        )

    def log_start(self, port):
        self.port = port
        message = 'start with {} port'.format(port)
        logging.info(message)

    def log_shutdown(self):
        message = 'shutdown {} port'.format(self.port)
        self.port = 0
        logging.info(message)

    def log_error(self, message: str):
        logging.info(message)
        print(message)

    def log_response(self, request_type: str, response_code: str,
                    headers: str, path: str, content: str):
        headers = headers.replace('\n', ' ')
        message = "{} request with {} response code\
        \n\tHeaders: {}\n\tPath: {}\n\tContent: {}".format(
            request_type,
            response_code,
            headers.replace('\n', ''),
            path,
            content
        )
        logging.info(message)