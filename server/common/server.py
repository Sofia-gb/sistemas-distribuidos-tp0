import socket
import logging
import sys
from common.communication_protocol import *
from common.utils import *

EXIT_CODE = 0

class Server:
    def __init__(self, port, listen_backlog, total_agencies):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._clients_sockets = []
        self.total_agencies = total_agencies
        self.waiting_agencies = {}

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

        for client_sock in self._clients_sockets:
            try:
                send_message(client_sock, Message.SERVER_SHUTDOWN.to_string())
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

    def get_winners(self):
        """ Get winners from bets """
        bets = load_bets()
        winners = {}
        for bet in bets:
            if has_won(bet):
                if bet.agency not in winners:
                    winners[bet.agency] = []
                winners[bet.agency].append(bet.document)
        return winners


    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        addr = client_sock.getpeername()

        while True:

            try:
                
                msg = receive_message(client_sock)
                
                logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
                msg_type = Message.from_string(msg)
                if msg_type == Message.CLIENT_SHUTDOWN:
                    try:
                        logging.info(f"action: disconnect_client | result: in_progress | ip: {addr[0]}")
                        client_sock.close()
                        logging.info(f"action: disconnect_client | result: success | ip: {addr[0]}")
                        self._clients_sockets.remove(client_sock)
                    except OSError as e:
                        logging.error(f"action: disconnect_client | result: fail | ip: {addr[0]} | error: {e.strerror}")
                    finally:
                        return
                    
                if msg_type == Message.BETS_SENT:
                    break
                    
                
                try:
                    bets = Bet.deserialize_bets(msg)
                    if len(bets) > 0 and bets[0].agency not in self.waiting_agencies:
                        agency = bets[0].agency
                        self.waiting_agencies[agency] = client_sock
                    store_bets(bets)
                    logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
                    send_message(client_sock, Message.SUCCESS.to_string())
                except ValueError as e:
                    logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                    send_message(client_sock, Message.FAIL.to_string())
                except OSError as e:
                    logging.error(f"action: send_message | result: fail | error: {e.strerror}")
                
            except OSError as e:
                logging.error(f"action: receive_message | result: fail | error: {e.strerror}")
                break

        if len(self.waiting_agencies) == self.total_agencies:
            logging.info("action: sorteo | result: success")
            winners = self.get_winners()
            for agency, socket in self.waiting_agencies.items():
                dni_winners = winners.get(agency, [])
                try:
                    msg = receive_message(socket)
                    logging.info(f'action: receive_message | result: success | agency: {agency} | msg: {msg}')
                    msg_type = Message.from_string(msg)
                    if msg_type == Message.GET_WINNERS:
                        try:                        
                            send_message(socket, Message.WINNERS.to_string(dni_winners))
                            logging.info(f"action: winners_sent | result: success | agency: {agency} | cantidad: {len(dni_winners)}")
                        except OSError as e:
                            logging.error(f"action: send_message | result: fail | error: {e.strerror}")
                    socket.close()
                    self._clients_sockets.remove(socket)
                except OSError as e:
                    logging.error(f"action: receive_message | result: fail | error: {e.strerror}")

            self.waiting_agencies = {}
            self.winners = {}
            logging.info(f"action: all_winners_sent | result: success")

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

