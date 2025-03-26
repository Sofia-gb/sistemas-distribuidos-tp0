package common

import (
	"fmt"
	"net"
	"strings"
)

const BYTES_TO_READ = 1
const MESSAGE_DELIMITER = '\n'

// SendMessage ensures the complete sending of a message (avoiding short-write)
func SendMessage(conn net.Conn, msg string) error {
	message := fmt.Sprintf("%s%c", msg, MESSAGE_DELIMITER)
	data := []byte(message)
	totalSent := 0

	for totalSent < len(data) {
		sent, err := conn.Write(data[totalSent:])
		if err != nil {
			return err
		}
		totalSent += sent
	}
	return nil
}

// ReceiveMessage ensures the complete reception of a message (avoiding short-read).
func ReceiveMessage(conn net.Conn) (string, error) {
	var buffer []byte

	for {
		byteChunk := make([]byte, BYTES_TO_READ)
		bytesRead, err := conn.Read(byteChunk)
		if err != nil {
			return "", fmt.Errorf("error receiving message: %w", err)
		}

		buffer = append(buffer, byteChunk[:bytesRead]...)

		if byteChunk[0] == MESSAGE_DELIMITER {
			break
		}
	}

	return string(buffer[:len(buffer)-1]), nil
}

// Message defines different types of messages.
type Message int

const (
	SUCCESS Message = iota
	FAIL
	SERVER_SHUTDOWN
	CLIENT_SHUTDOWN
	BETS_SENT
	GET_WINNERS
	WINNERS
	UNKNOWN
)

// ToString casts Message to string.
func (r Message) ToString(dnis ...string) string {
	switch r {
	case SUCCESS:
		return "SUCCESS"
	case FAIL:
		return "FAIL"
	case SERVER_SHUTDOWN:
		return "SERVER_SHUTDOWN"
	case CLIENT_SHUTDOWN:
		return "CLIENT_SHUTDOWN"
	case BETS_SENT:
		return "BETS_SENT"
	case GET_WINNERS:
		return "GET_WINNERS"
	case WINNERS:
		return fmt.Sprintf("WINNERS:%s", strings.Join(dnis, ","))
	default:
		return "UNKNOWN"
	}
}

// NewMessage creates a Message from a string.
func NewMessage(s string) Message {
	if strings.HasPrefix(s, "WINNERS:") {
		return WINNERS
	}

	switch s {
	case "SUCCESS":
		return SUCCESS
	case "FAIL":
		return FAIL
	case "SERVER_SHUTDOWN":
		return SERVER_SHUTDOWN
	case "CLIENT_SHUTDOWN":
		return CLIENT_SHUTDOWN
	case "BETS_SENT":
		return BETS_SENT
	case "GET_WINNERS":
		return GET_WINNERS
	default:
		return UNKNOWN
	}
}
