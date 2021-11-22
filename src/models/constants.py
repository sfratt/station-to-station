HOST = '127.0.0.1' # Localhost
PORT = 65341
ADDR = (HOST, PORT)

BUFFER_SIZE = 2048
FORMAT = 'utf-8'
METHOD_HEADER_SIZE = 25
LENGTH_HEADER_SIZE = 10
TYPE_HEADER_SIZE = 9
ENCODING_HEADER_SIZE = 6

HEADER_SIZE = METHOD_HEADER_SIZE + LENGTH_HEADER_SIZE + TYPE_HEADER_SIZE + ENCODING_HEADER_SIZE + 58