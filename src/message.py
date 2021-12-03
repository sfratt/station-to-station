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
        """
        Function to create the request to send to the server
        """
        body = json.dumps(payload, indent=2)
        content_length = len(body.encode(FORMAT))
        content_type = 'text/json'
        content_encoding = FORMAT

        # Using fixed length header
        request = f'{method:<{METHOD_HEADER_SIZE}}\r\nContent-Length: {content_length:<{LENGTH_HEADER_SIZE}}\r\nContent-Type: {content_type:<{TYPE_HEADER_SIZE}}\r\nContent-Encoding: {content_encoding:<{ENCODING_HEADER_SIZE}}\r\n\r\n{body}'

        return request.encode(FORMAT)

    def create_response(self, payload, status_code: int):
        """
        Function to create the response of the server to the user
        """
        body = json.dumps(payload, indent=2)
        content_length = len(body.encode(FORMAT))
        content_type = 'text/json'
        content_encoding = FORMAT

        phrase = STATUS_CODES[str(status_code)]
        status = f'{status_code} {phrase}'

        # Using fixed length header
        response = f'{status:<{METHOD_HEADER_SIZE}}\r\nContent-Length: {content_length:<{LENGTH_HEADER_SIZE}}\r\nContent-Type: {content_type:<{TYPE_HEADER_SIZE}}\r\nContent-Encoding: {content_encoding:<{ENCODING_HEADER_SIZE}}\r\n\r\n{body}'

        return response.encode(FORMAT)

    def extract_method(self, message: str):
        """
        Function to extract the function called by the user
        """
        method = message.split('\r\n')[0].strip()

        return method.lower().replace('-', '_')
        
    def extract_headers(self, message: str):
        """
        Function to extract information from the response such as content length, content type and content encoding
        """
        message_split = message.split('\r\n')
        matches = [message.split(':')[1].strip() for message in message_split[1:4]]    
        content_dict = {
            "content-length": int(matches[0]),
            "content-type": matches[1],
            "content-encoding": matches[2]
        }
        
        return content_dict

    def extract_body(self, message: str):
        """
        Function to extract the body of the response and request
        """
        body = message.split('\r\n\r\n')[1]
        
        return json.loads(body)


message = Message()