import socket
import logging
from common.communication_protocol import *
from common.utils import *
import threading

class Server:
    def __init__(self, port, listen_backlog, total_agencies):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._clients_sockets = []
        self._agencies_waiting = {}
        self._lock = threading.Lock()
        self._clients_threads = []
        self._barrier_bets_received = threading.Barrier(total_agencies)
        self._total_agencies = total_agencies

    def run(self):
        """
        Creates a new thread for each client connection. The thread will receive and send messages
        to the given agency, using a socket. 
        
        The main thread will wait for all the threads to finish before closing the server
        """
        agencies = 0

        while agencies < self._total_agencies:
            try:
                client_sock = self.__accept_new_connection()
                self._clients_sockets.append(client_sock)
                client_thread = threading.Thread(target=self.__handle_client_connection, args=(client_sock,))
                client_thread.start()
                self._clients_threads.append(client_thread)
                agencies += 1
            except OSError as e:
                logging.warning(f"action: accept_connections | result: fail | error: {e.strerror}")
                break

        self.__wait_for_clients_threads()

    def close(self):
        """
        Closes server socket and client sockets, and wait for all threads to finish.
        """

        logging.info("action: shutdown | result: in_progress")
        for client_sock in self._clients_sockets:
            try:
                send_message(client_sock, Message.SERVER_SHUTDOWN.to_string())
                addr = client_sock.getpeername()
                logging.info(f"action: send_shutdown_message | result: success | ip: {addr[0]}")
            except OSError as e:
                logging.error(f"action: send_shutdown_message | result: fail | error: {e.strerror}")
            finally:
                self.__disconnect_client(client_sock)

        self._clients_sockets = []

        try:
            logging.info(f"action: close_server_socket | result: in_progress")
            self._server_socket.close()
            logging.info(f"action: close_server_socket | result: success")

        except OSError as e:
            logging.error(f"action: close_server_socket | result: fail | error: {e.strerror}")

        self.__wait_for_clients_threads()
            
        logging.info("action: shutdown | result: success")

    def __wait_for_clients_threads(self):
        """ Waits for all threads to finish. It will remove the threads from the list of threads """
        for thread in self._clients_threads:
            logging.info(f"action: join_thread | result: in_progress | thread: {thread.name}")
            thread.join()
            self._clients_threads.remove(thread)
            logging.info(f"action: join_thread | result: success | thread: {thread.name}")

    def __get_winners(self, client_sock):
        """ Get winners from bets. Each thread will get the winners of the agency it is handling """
        with self._lock:
            agency = self._agencies_waiting[client_sock]
            bets = load_bets()
        winners = []
        for bet in bets:
            if bet.agency == agency and has_won(bet):
                winners.append(bet.document)
        return winners


    def __handle_client_connection(self, client_sock):
        """
        It receives bets from the client and stores them in a file, notifying the client whether the operation was 
        successful or not. Then it gets the winners of the agency and notifies the client sending the winners.

        """

        self.__receive_bets(client_sock)

        try:
            self._barrier_bets_received.wait() 

        except threading.BrokenBarrierError:
            logging.error("action: sorteo | result: fail | reason: barrier broken")
            return

        logging.info("action: sorteo | result: success")
        winners = self.__get_winners(client_sock)
        self.__notify_winners(winners, client_sock)

    def __notify_winners(self, dni_winners, socket):
        """Sends to agency N the winners of agency N if it is still connected and asks for them.
         Each thread will send to the agency it is handling its winners."""
        
        with self._lock:
            agency = self._agencies_waiting[socket]
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
            with self._lock:
                self.__disconnect_client(socket)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e.strerror}")

    def __receive_bets(self, client_sock):
        """
        Receives bets from a client until the agency sends a CLIENT_SHUTDOWN message or a BETS_SENT message
        """

        while True:
            try:
                addr = client_sock.getpeername()
                msg = receive_message(client_sock)
                
                logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
                msg_type = Message.from_string(msg)
                if msg_type == Message.CLIENT_SHUTDOWN:
                    with self._lock:
                        self.__disconnect_client(client_sock)
                    break
                    
                if msg_type == Message.BETS_SENT:
                    break
                                  
                self.__store_bets(client_sock, msg)
                
            except OSError as e:
                logging.error(f"action: receive_message | result: fail | error: {e.strerror}")
                break

    def __store_bets(self, client_sock, msg):
        """ Stores bets in the storage file and notifies the client whether the operation was successful or not """
        try:
            bets = Bet.deserialize_bets(msg)
            with self._lock:
                if len(bets) > 0 and bets[0].agency not in self._agencies_waiting:
                    agency = bets[0].agency
                    self._agencies_waiting[client_sock] = agency
                    threading.current_thread().name = "Thread-" + str(agency)
                store_bets(bets)
            logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
            send_message(client_sock, Message.SUCCESS.to_string())
        except ValueError as e:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
            send_message(client_sock, Message.FAIL.to_string())
        except OSError as e:
            logging.error(f"action: send_message | result: fail | error: {e.strerror}")

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
        finally:
            if client_sock in self._clients_sockets:
                self._clients_sockets.remove(client_sock)
