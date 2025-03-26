from enum import Enum

BYTES_TO_READ = 1
MESSAGE_DELIMITER = "\n"
DNIS_DELIMITER = ","

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
    """Ensures the complete sending of a message (avoiding short-write)."""
    msg = f"{msg}{MESSAGE_DELIMITER}".encode('utf-8') 
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
        chunk = socket.recv(BYTES_TO_READ)
        if not chunk:
            raise OSError("Connection broken")
        
        buffer.extend(chunk)
        if buffer[-1] == ord(MESSAGE_DELIMITER):  
            break

    return buffer.decode('utf-8').strip() 