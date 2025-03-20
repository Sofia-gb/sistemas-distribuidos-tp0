import socket
from enum import Enum

class Message(Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    SERVER_SHUTDOWN = "SERVER_SHUTDOWN"
    CLIENT_SHUTDOWN = "CLIENT_SHUTDOWN"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def from_string(msg: str):
        msg = msg.strip()  
        return Message.__members__.get(msg, Message.UNKNOWN)


def send_message(conn: socket.socket, msg: str):
    """Ensures the complete sending of a message (avoiding short-write)."""
    msg = f"{msg}\n".encode('utf-8') 
    total_sent = 0

    while total_sent < len(msg):
        sent = conn.send(msg[total_sent:])
        if sent == 0:
            raise RuntimeError("Connection broken")
        total_sent += sent


def receive_message(conn: socket.socket) -> str:
    """Ensures the complete reception of a message (avoiding short-read)."""
    buffer = bytearray()
    
    while True:
        chunk = conn.recv(1024)
        if not chunk:
            raise RuntimeError("Connection broken")
        
        buffer.extend(chunk)
        if buffer[-1] == ord("\n"):  
            break

    return buffer.decode('utf-8').strip() 