import socket
import logging
from common.communication_protocol import *
from common.utils import *
import multiprocessing

class Server:
    def __init__(self, port, listen_backlog, total_agencies):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._clients_processes = []
        self._total_agencies = total_agencies
        self._barrier_bets_received = multiprocessing.Barrier(total_agencies)
        self._client_socket = None
        self._agency_waiting = None
        self._lock = multiprocessing.Lock() 
        self._name = multiprocessing.current_process().name

    def run(self):
        """
        Creates a new proces for each client connection. The proces will receive and send messages
        to the given agency, using a socket. 
        
        The main proces will wait for all the processes to finish before closing the server
        """
        agencies = 0

        while agencies < self._total_agencies:
            try:
                client_sock = self.__accept_new_connection()
                client_process = multiprocessing.Process(target=self.__handle_client_connection, args=(client_sock,))
                client_process.start()
                self.__close_client_socket(client_sock)
                self._clients_processes.append(client_process)
                agencies += 1
            except OSError as e:
                logging.warning(f"action: accept_connections | result: fail | error: {e.strerror} | process: {self._name}")
                break

        self.close()

    def close(self):
        """
        Closes server socket and client sockets, and wait for all processes to finish.
        """

        logging.info(f"action: shutdown | result: in_progress | process: {self._name}")
        self.__wait_for_clients_processes()
        self.__close_client_socket(must_notify=True)
        self.__close_server_socket()
            
        logging.info("action: shutdown | result: success")

    def __wait_for_clients_processes(self):
        """ Waits for all processes to finish. It will remove the process from the list of processes """
        for process in self._clients_processes:
            logging.info(f"action: join_process | result: in_progress | target: {process.name} | process: {self._name}")
            process.join()
            self._clients_processes.remove(process)
            logging.info(f"action: join_process | result: success | target: {process.name} | process: {self._name}")

    def __get_winners(self):
        """ Get winners from bets. Each process will get the winners of the agency it is handling """
        agency = self._agency_waiting
        with self._lock:
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
        self._name = multiprocessing.current_process().name
        self.__close_server_socket()
        self._client_socket = client_sock
        self.__receive_bets()
        if self._client_socket is None: # client disconnected
            return

        try:
            self._barrier_bets_received.wait() 

        except RuntimeError as e:
            logging.error(f"action: sorteo | result: fail | error: barrier broken | process: {self._name}")
            return

        logging.info(f"action: sorteo | result: success | process: {self._name}")
        winners = self.__get_winners()
        self.__notify_winners(winners)

    def __notify_winners(self, dni_winners):
        """Sends to agency N the winners of agency N if it is still connected and asks for them.
         Each process will send to the agency it is handling its winners."""
        socket = self._client_socket
        agency = self._agency_waiting
        try:
            msg = receive_message(socket)
            logging.info(f'action: receive_message | result: success | agency: {agency} | msg: {msg} | process: {self._name}')
            msg_type = Message.from_string(msg)
            if msg_type == Message.GET_WINNERS:
                try:                        
                    send_message(socket, Message.WINNERS.to_string(dni_winners))
                    logging.info(f"action: winners_sent | result: success | agency: {agency} | cantidad: {len(dni_winners)} | process: {self._name}")
                except OSError as e:
                    logging.error(f"action: send_message | result: fail | error: {e.strerror} | process: {self._name}")
            self.__close_client_socket(socket)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e.strerror} | process: {self._name}")

    def __receive_bets(self):
        """
        Receives bets from a client until the agency sends a CLIENT_SHUTDOWN message or a BETS_SENT message
        """
        client_sock = self._client_socket

        while True:
            try:
                addr = client_sock.getpeername()
                msg = receive_message(client_sock)
                
                logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg} | process: {self._name}')
                msg_type = Message.from_string(msg)
                if msg_type == Message.CLIENT_SHUTDOWN:
                    self.__close_client_socket()
                    break
                    
                if msg_type == Message.BETS_SENT:
                    break
                                  
                self.__store_bets(msg)
                
            except OSError as e:
                logging.error(f"action: receive_message | result: fail | error: {e.strerror} | process: {self._name}")
                break

    def __store_bets(self, msg):
        """ Stores bets in the storage file and notifies the client whether the operation was successful or not """
        client_sock = self._client_socket
        try:
            bets = Bet.deserialize_bets(msg)
            if self._agency_waiting is None and len(bets) > 0:
                self._agency_waiting = bets[0].agency
            with self._lock:
                store_bets(bets)
            logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)} | process: {self._name}")
            send_message(client_sock, Message.SUCCESS.to_string())
        except ValueError as e:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}   | process: {self._name}")
            send_message(client_sock, Message.FAIL.to_string())
        except OSError as e:
            logging.error(f"action: send_message | result: fail | error: {e.strerror} | process: {self._name}")

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info(f'action: accept_connections | result: in_progress | process: {self._name}')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]} | process: {self._name}')
        return c

    def __close_client_socket(self, socket=None, must_notify=False):
        """
        Disconnect client socket. It closes the client socket and removes it from the
        list of client sockets
        """
        client_sock = socket if socket is not None else self._client_socket
        if client_sock is None: return
        if must_notify:
            try:
                send_message(client_sock, Message.SERVER_SHUTDOWN.to_string())
                addr = client_sock.getpeername()
                logging.info(f"action: send_shutdown_message | result: success | ip: {addr[0]} | process: {self._name}")
            except OSError as e:
                logging.error(f"action: send_shutdown_message | result: fail | error: {e.strerror} | process: {self._name}")
        try:
            addr = client_sock.getpeername()
            logging.info(f"action: close_client_socket | result: in_progress | ip: {addr[0]} | process: {self._name}")
            client_sock.close()
            logging.info(f"action: close_client_socket | result: success | ip: {addr[0]} | process: {self._name}")
        except OSError as e:
            # Ignore the exception and do nothing (logging the error is not compatible with the tests)
            pass
        finally:
            self._client_sock = None

    def __close_server_socket(self):
        """
        Disconnect server socket. It closes the server socket
        """
        if self._server_socket is None: return
        try: 
            logging.info(f"action: close_server_socket | result: in_progress | process: {self._name}")
            self._server_socket.close()
            logging.info(f"action: close_server_socket | result: success | process: {self._name}")
        except OSError as e:
            logging.error(f"action: close_server_socket | result: fail | error: {e.strerror} | process: {self._name}")
        finally:
            self._server_socket = None