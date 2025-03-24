from enum import Enum

MAX_PACKET_SIZE = 8192

class Message(Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    SERVER_SHUTDOWN = "SERVER_SHUTDOWN"
    CLIENT_SHUTDOWN = "CLIENT_SHUTDOWN"
    UNKNOWN = "UNKNOWN"
    BETS_SENT = "BETS_SENT"
    GET_WINNERS = "GET_WINNERS"

    @staticmethod
    def from_string(msg: str):
        msg = msg.strip()  
        return Message.__members__.get(msg, Message.UNKNOWN)


def send_message(socket, msg):
    """Ensures the complete sending of a message (avoiding short-write)."""
    msg = f"{msg}\n".encode('utf-8') 
    total_sent = 0

    while total_sent < len(msg):
        sent = socket.send(msg[total_sent:])
        if sent == 0:
            raise OSError("Connection broken")
        total_sent += sent


def receive_message(socket):
    """Ensures the complete reception of a message (avoiding short-read)."""
    buffer = bytearray()
    
    while True:
        chunk = socket.recv(MAX_PACKET_SIZE)
        if not chunk:
            raise OSError("Connection broken")
        
        buffer.extend(chunk)
        if buffer[-1] == ord("\n"):  
            break

    return buffer.decode('utf-8').strip() 