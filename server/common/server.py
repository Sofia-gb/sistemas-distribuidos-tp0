import socket
import logging
import sys

EXIT_CODE = 0

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

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        while True:
            client_sock = self.__accept_new_connection()
            self._clients_sockets.append(client_sock)
            self.__handle_client_connection(client_sock)

    def close(self):
        """
        Close server socket and all client sockets
        """

        logging.info("action: shutdown | result: in_progress")

        shutdown_message = "SERVER_SHUTDOWN\n".encode("utf-8")
        for client_sock in self._clients_sockets:
            try:
                client_sock.send(shutdown_message)
                addr = client_sock.getpeername()
                logging.info(f"action: send_shutdown_message | result: success | ip: {addr[0]}")
                logging.info(f"action: disconnect_client | result: in_progress | ip: {addr[0]}")

            except OSError as e:
                logging.error(f"action: disconnect_client | result: fail | error: {e.strerror}")

            finally:
                client_sock.close()
                logging.info(f"action: disconnect_client | result: success | ip: {addr[0]}")

        self._clients_sockets = []

        try:
            logging.info(f"action: close_server_socket | result: in_progress")
            self._server_socket.close()
            logging.info(f"action: close_server_socket | result: success")

        except OSError as e:
            logging.error(f"action: close_server_socket | result: fail | error: {e.strerror}")
  
        logging.info("action: shutdown | result: success")
        sys.exit(EXIT_CODE)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            msg = client_sock.recv(1024).rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')

            if msg == "CLIENT_SHUTDOWN":
                try:
                    logging.info(f"action: disconnect_client | result: in_progress | ip: {addr[0]}")
                    client_sock.close()
                    logging.info(f"action: disconnect_client | result: success | ip: {addr[0]}")
                    self._clients_sockets.remove(client_sock)
                except OSError as e:
                    logging.error(f"action: disconnect_client | result: fail | ip: {addr[0]} | error: {e.strerror}")
                finally:
                    return

            # TODO: Modify the send to avoid short-writes
            client_sock.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()
            self._clients_sockets.remove(client_sock)

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
