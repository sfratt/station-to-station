import json

VERSION = 'HTTP/1.0'
FORMAT = 'utf-8'
STATUS_CODES = {
    '200': 'OK', 
    '400': 'Bad Request', 
    '401': 'Unauthorized', 
    '403': 'Forbidden', 
    '404': 'Not Found', 
    '500': 'Internal Server Error', 
    '502': 'Bad Gateway', 
    '503': 'Service Unavailable'
}

class Message:

    def __init__(self):
        pass

    def create_request(self, method: str, url: str, payload):
        body = json.dumps(payload)
        content_length = len(body.encode(FORMAT))
        content_type = 'text/json' # text/json or text/string or binary
        content_encoding = 'utf-8' # utf-8 or binary

        request = '{} {} {}\r\nContent-Length: {}\r\nContent-Type: {}\r\nContent-Encoding: {}\r\n\r\n{}'.format(method, url, VERSION, content_length, content_type, content_encoding, body)
        # print('[REQUEST CREATED] Request message:\n{}'.format(request))

        return request.encode(FORMAT)

    def create_response(self, payload, status_code: int):
        body = json.dumps(payload)
        content_length = len(body.encode(FORMAT))
        content_type = 'text/json' # text/json or text/string or binary
        content_encoding = 'utf-8' # utf-8 or binary

        phrase = STATUS_CODES[str(status_code)]

        response = '{} {} {}\r\nContent-Length: {}\r\nContent-Type: {}\r\nContent-Encoding: {}\r\n\r\n{}'.format(VERSION, status_code, phrase, content_length, content_type, content_encoding, body)
        # print('[RESPONSE CREATED] Response message:\n{}'.format(response))

        return response.encode(FORMAT)

    def extract_url(self) -> str:
        pass

    def extract_headers(self) -> dict:
        pass

    def extract_body(self) -> dict:
        pass


message = Message()

# TESTs
message.create_request('GET', '/test', {'test': '123'})
message.create_response({'ACK': True}, 200)