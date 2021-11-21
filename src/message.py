import json

from models.constants import FORMAT, METHOD_HEADER_SIZE, LENGTH_HEADER_SIZE, TYPE_HEADER_SIZE, ENCODING_HEADER_SIZE

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

    def create_request(self, method: str, payload):
        body = json.dumps(payload)
        content_length = len(body.encode(FORMAT))
        content_type = 'text/json' # text/json or text/string or binary
        content_encoding = 'utf-8' # utf-8 or binary

        request = f'{method:<{METHOD_HEADER_SIZE}}\r\nContent-Length: {content_length:<{LENGTH_HEADER_SIZE}}\r\nContent-Type: {content_type:<{TYPE_HEADER_SIZE}}\r\nContent-Encoding: {content_encoding:<{ENCODING_HEADER_SIZE}}\r\n\r\n{body}' # Create a fixed length msg
        # print('[REQUEST CREATED] Request message:\n{}'.format(request))

        return request.encode(FORMAT)

    def create_response(self, payload, status_code: int):
        body = json.dumps(payload)
        content_length = len(body.encode(FORMAT))
        content_type = 'text/json' # text/json or text/string or binary
        content_encoding = 'utf-8' # utf-8 or binary

        phrase = STATUS_CODES[str(status_code)]

        response = '{} {}\r\nContent-Length: {}\r\nContent-Type: {}\r\nContent-Encoding: {}\r\n\r\n{}'.format(status_code, phrase, content_length, content_type, content_encoding, body)
        # print('[RESPONSE CREATED] Response message:\n{}'.format(response))

        return response.encode(FORMAT)

    def extract_method(self, message: str):
        method = message.split('\r\n')[0].strip()

        return method.lower().replace('-', '_')
        
    def extract_headers(self, message: str):
        message_split = message.split('\r\n')
        matches = [message.split(':')[1].strip() for message in message_split[1:4]] # Change to accept dynamic number of headers, not just 3     
        content_dict = {
            "content-length": int(matches[0]),
            "content-type": matches[1],
            "content-encoding": matches[2]
        }
        
        return content_dict

    def extract_body(self, message: str):
        body = message.split('\r\n\r\n')[1]
        
        return json.loads(body)


message = Message()

# TESTs
# message.create_request('TEST-METHOD', {'test': '123'})
# message.create_response({'ACK': True}, 200)