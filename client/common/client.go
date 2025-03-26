package common

import (
	"bufio"
	"net"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

const SLEEP_TIME = 1000 * time.Millisecond

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID             string
	ServerAddress  string
	LoopAmount     int
	LoopPeriod     time.Duration
	BetsFile       string
	BatchMaxAmount int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	bets   []*Bet
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	bets := CreateBetsFromCSV(config)
	client := &Client{
		config: config,
		bets:   bets,
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
		return err
	}
	c.conn = conn
	return nil
}

// StartClient sends bets in batches to the server and waits for the response.
func (c *Client) StartClient() {
	err := c.createClientSocket()
	if err != nil {
		return
	}

	batches := CreateBetsInBatches(c.bets, c.config.BatchMaxAmount)

	for _, batch := range batches {

		err := SendMessage(c.conn, batch.Serialize())

		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v", c.config.ID, err)
			break
		}

		msg, err := ReceiveMessage(c.conn)

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v", c.config.ID, err)
			break
		}

		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v", c.config.ID, msg)

		msgType := NewMessage(msg)

		switch msgType {
		case SUCCESS:
			log.Infof("action: apuesta_enviada | result: success | agencia: %v | cantidad: %v",
				c.config.ID,
				batch.Size(),
			)
		case SERVER_SHUTDOWN:
			c.Close()
			return
		default:
			log.Errorf("action: apuesta_enviada | result: fail | agencia: %v | cantidad: %v",
				c.config.ID,
				batch.Size(),
			)
		}
	}
	c.Close()
}

// Close gracefully shuts down the client by closing the socket connection.
func (c *Client) Close() {
	log.Infof("action: shutdown | result: in_progress | client_id: %v", c.config.ID)
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
	log.Infof("action: shutdown | result: success | client_id: %v", c.config.ID)
	time.Sleep(SLEEP_TIME)
}

// CreateBetsFromCSV Lee el archivo CSV y crea una lista de apuestas
func CreateBetsFromCSV(config ClientConfig) []*Bet {
	file, err := os.Open(config.BetsFile)
	var bets []*Bet
	if err != nil {
		log.Errorf("action: read_csv_file | result: fail | client_id: %v | error: %v", config.ID, err)
		return bets
	}
	defer closeBetsFile(file)

	scanner := bufio.NewScanner(file)

	for scanner.Scan() {
		line := scanner.Text()
		betData := strings.Split(line, ",")

		if len(betData) != 5 {
			log.Warningf("action: parse_bet | result: fail | reason: incorrect format | line: %v", line)
			continue
		}

		firstName := betData[0]
		lastName := betData[1]
		dni := betData[2]
		birthDate := betData[3]
		amount, err := strconv.Atoi(betData[4])
		if err != nil {
			log.Errorf("action: parse_bet_amount | result: fail | client_id: %v | error: %v", config.ID, err)
			continue
		}

		bet := NewBet(config.ID, firstName, lastName, birthDate, dni, amount)
		bets = append(bets, bet)
	}
	log.Infof("action: read_csv_file | result: success | client_id: %v | cantidad: %v", config.ID, len(bets))
	return bets
}

func closeBetsFile(file *os.File) {
	err := file.Close()
	if err != nil {
		log.Errorf("action: close_csv | result: fail | error: %v", err)
	} else {
		log.Infof("action: close_csv | result: success")
	}
}
