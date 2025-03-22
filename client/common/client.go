package common

import (
	"net"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
	Name          string
	Surname       string
	Bet           int
	BirthDate     string
	DNI           string
	BetsFile      string
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	bet    *Bet
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
		bet:    NewBet(config),
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClient sends the bet to the server and waits for the response.
func (c *Client) StartClient() {
	c.createClientSocket()

	SendMessage(c.conn, c.bet.Serialize())

	msg, err := ReceiveMessage(c.conn)

	c.conn.Close()

	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}

	log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
		c.config.ID,
		msg,
	)

	msgType := NewMessage(msg)

	switch msgType {
	case SUCCESS:
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			c.config.DNI,
			c.config.Bet,
		)
	case SERVER_SHUTDOWN:
		c.Close()
	default:
		log.Errorf("action: apuesta_enviada | result: fail | dni: %v | numero: %v",
			c.config.DNI,
			c.config.Bet,
		)
	}
}

// Close gracefully shuts down the client by closing the socket connection.
func (c *Client) Close() {
	log.Infof("action: close_connection | result: in_progress | client_id: %v", c.config.ID)
	if c.conn != nil {
		err := SendMessage(c.conn, Message(CLIENT_SHUTDOWN).ToString())
		if err != nil {
			log.Warningf("action: send_shutdown_message | result: fail | client_id: %v | error: %v", c.config.ID, err)
		} else {
			log.Infof("action: send_shutdown_message | result: success | client_id: %v", c.config.ID)
		}
		err = c.conn.Close()
		if err != nil {
			log.Errorf("action: close_connection | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
		} else {
			log.Infof("action: close_connection | result: success | client_id: %v", c.config.ID)
		}
	}
}
