package common

import (
	"encoding/binary"
	"fmt"
	"net"
	"strings"
)

const MESSAGE_DELIMITER = '\n'
const SIZE_BYTES = 4

// SendMessage ensures the complete sending of a message (avoiding short-write).
// The final message is composed of a 4-byte header with the message size and the message itself.
func SendMessage(conn net.Conn, msg string) error {
	message := fmt.Sprintf("%s%c", msg, MESSAGE_DELIMITER)
	data := []byte(message)
	msgSize := uint32(len(data))
	header := make([]byte, SIZE_BYTES)
	binary.BigEndian.PutUint32(header, msgSize)

	completeMsg := append(header, data...)
	totalSent := 0

	for totalSent < len(completeMsg) {
		sent, err := conn.Write(completeMsg[totalSent:])
		if err != nil {
			return err
		}
		totalSent += sent
	}
	return nil
}

// ReceiveMessage ensures the complete reception of a message (avoiding short-read).
// Receives a message composed of a 4-byte header with the message size and the message itself.
func ReceiveMessage(conn net.Conn) (string, error) {
	header, err := recvHeader(conn)
	if err != nil {
		return "", fmt.Errorf("error receiving message: %w", err)
	}

	msgSize_uint := binary.BigEndian.Uint32(header)

	buffer, err := recvMessage(msgSize_uint, conn)
	if err != nil {
		return "", fmt.Errorf("error receiving message: %w", err)
	}

	return string(buffer[:len(buffer)-1]), nil
}

// recvMessage ensures the complete reception of a message (avoiding short-read).
// The message size is given as an argument.
func recvMessage(msgSize_uint uint32, conn net.Conn) ([]byte, error) {
	var buffer []byte
	totalRead := 0
	msgSize := int(msgSize_uint)

	for totalRead < msgSize {
		byteChunk := make([]byte, msgSize-totalRead)
		n, err := conn.Read(byteChunk)
		if err != nil {
			return nil, err
		}
		totalRead += n
		buffer = append(buffer, byteChunk[:n]...)
	}
	if buffer[len(buffer)-1] != MESSAGE_DELIMITER {
		return nil, fmt.Errorf("message delimiter not found")
	}
	return buffer, nil
}

// recvHeader ensures the complete reception of a message header (avoiding short-read).
// The header is composed of a 4-byte message size.
func recvHeader(conn net.Conn) ([]byte, error) {
	header := make([]byte, SIZE_BYTES)
	totalRead := 0

	for totalRead < SIZE_BYTES {
		bytesRead, err := conn.Read(header[totalRead:])
		if err != nil {
			return nil, err
		}
		totalRead += bytesRead
	}
	return header, nil
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
