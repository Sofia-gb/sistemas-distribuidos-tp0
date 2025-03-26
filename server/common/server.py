import socket
import logging
from common.communication_protocol import *
from common.utils import *

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._clients_sockets = []

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while True:
            try:
                client_sock = self.__accept_new_connection()
                self._clients_sockets.append(client_sock)
                self.__handle_client_connection(client_sock)
            except OSError as e:
                logging.warning(f"action: accept_connections | result: fail | error: {e.strerror}")
                break

    def close(self):
        """
        Close server socket and all client sockets
        """

        logging.info("action: shutdown | result: in_progress")

        for client_sock in self._clients_sockets:
            try:
                send_message(client_sock, Message.SERVER_SHUTDOWN.value)
                addr = client_sock.getpeername()
                logging.info(f"action: send_shutdown_message | result: success | ip: {addr[0]}")
                self.__disconnect_client(client_sock)
            except OSError as e:
                logging.error(f"action: send_shutdown_message | result: fail | error: {e.strerror}")
        
        self._clients_sockets = []

        try:
            logging.info(f"action: close_server_socket | result: in_progress")
            self._server_socket.close()
            logging.info(f"action: close_server_socket | result: success")

        except OSError as e:
            logging.error(f"action: close_server_socket | result: fail | error: {e.strerror}")
  
        logging.info("action: shutdown | result: success")

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        while True:

            try:
                addr = client_sock.getpeername()
                msg = receive_message(client_sock)
                
                logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
                msg_type = Message.from_string(msg)
                if msg_type == Message.CLIENT_SHUTDOWN:
                    self.__disconnect_client(client_sock)
                    break
                
                try:
                    bets = Bet.deserialize_bets(msg)
                    store_bets(bets)
                    logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
                    send_message(client_sock, Message.SUCCESS.value)
                except ValueError as e:
                    logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                    send_message(client_sock, Message.FAIL.value)
                except OSError as e:
                    logging.error(f"action: send_message | result: fail | error: {e.strerror}")
                
            except OSError as e:
                logging.error(f"action: receive_message | result: fail | error: {e.strerror}")
                break
            
        self.__disconnect_client(client_sock)

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c

    def __disconnect_client(self, client_sock):
        """
        Disconnect client socket. It closes the client socket and removes it from the
        list of client sockets
        """

        try:
            addr = client_sock.getpeername()
            logging.info(f"action: disconnect_client | result: in_progress | ip: {addr[0]}")
            client_sock.close()
            logging.info(f"action: disconnect_client | result: success | ip: {addr[0]}")
        except OSError as e:
            logging.error(f"action: disconnect_client | result: fail | ip: {addr[0]} | error: {e.strerror}")
        finally:
            if client_sock in self._clients_sockets:
                self._clients_sockets.remove(client_sock)
