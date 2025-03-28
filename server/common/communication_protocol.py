from enum import Enum

MESSAGE_DELIMITER = "\n"
DNIS_DELIMITER = ","
SIZE_BYTES = 4

class Message(Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    SERVER_SHUTDOWN = "SERVER_SHUTDOWN"
    CLIENT_SHUTDOWN = "CLIENT_SHUTDOWN"
    UNKNOWN = "UNKNOWN"
    BETS_SENT = "BETS_SENT"
    GET_WINNERS = "GET_WINNERS"
    WINNERS = "WINNERS"

    @staticmethod
    def from_string(msg: str):
        msg = msg.strip()  
        return Message.__members__.get(msg, Message.UNKNOWN)
    
    def to_string(self, *args):
        if self == Message.WINNERS:
            dnis = args[0]
            return f"{self.value}:{DNIS_DELIMITER.join(dnis)}"
        return self.value
    

def send_message(socket, msg):
    """Ensures the complete sending of a message (avoiding short-write).
    The final message is composed of a 4-byte header with the message size and the message itself."""
    msg = f"{msg}{MESSAGE_DELIMITER}".encode('utf-8') 
    msg_size = len(msg).to_bytes(SIZE_BYTES, byteorder='big')
    complete_msg = msg_size + msg
    total_sent = 0

    while total_sent < len(complete_msg):
        sent = socket.send(complete_msg[total_sent:])
        if sent == 0:
            raise OSError("Connection broken")
        total_sent += sent


def receive_message(socket):
    """Ensures the complete reception of a message (avoiding short-read).
    Receives a message composed of a 4-byte header with the message size and the message itself."""

    msg_size = __recv_message_size(socket)
    buffer = __recv_message(socket, msg_size)
    return buffer.decode('utf-8').rstrip(MESSAGE_DELIMITER) 

def __recv_message(socket, msg_size):
    """Receives the message from the socket.
    The message size is given by the msg_size parameter."""
    buffer = bytearray()
    while len(buffer) < msg_size:
        chunk = socket.recv(msg_size - len(buffer))
        if not chunk:
            raise OSError("Connection broken")
        buffer.extend(chunk)
    if buffer[-1] != ord(MESSAGE_DELIMITER):  
        raise OSError("Connection broken")
    return buffer

def __recv_message_size(socket):
    """ Receives the message size from the socket. """
    msg_size_buffer = bytearray()
    while len(msg_size_buffer) < SIZE_BYTES:
        chunk = socket.recv(SIZE_BYTES - len(msg_size_buffer))
        if not chunk:
            raise OSError("Connection broken")
        msg_size_buffer.extend(chunk)
    msg_size = int.from_bytes(msg_size_buffer, byteorder='big')
    return msg_size