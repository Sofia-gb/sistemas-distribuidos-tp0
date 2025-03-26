package common

import (
	"fmt"
	"strings"
)

const MAX_PACKET_SIZE = 8192
const BETS_DELIMITER = ";"

// Bet Entity encapsulates information abount an specific bet
type Bet struct {
	agency     string
	first_name string
	last_name  string
	number     int
	birthDate  string
	dni        string
}

// Serialize Returns a string representation of the Bet entity with the following format:
// AGENCY=agency,FIRST_NAME=first_name,LAST_NAME=last_name,NUMBER=number,BIRTH_DATE=birthDate,DNI=dni
func (b *Bet) Serialize() string {
	return fmt.Sprintf("AGENCY=%s,FIRST_NAME=%s,LAST_NAME=%s,NUMBER=%d,BIRTH_DATE=%s,DNI=%s", b.agency, b.first_name, b.last_name, b.number, b.birthDate, b.dni)
}

// DeserializeBet Receives a string with the following format
// AGENCY=agency,FIRST_NAME=first_name,LAST_NAME=last_name,NUMBER=number,BIRTH_DATE=birthDate,DNI=dni
// and returns a Bet entity
func DeserializeBet(betString string) *Bet {
	var agency, name, surname, birthDate, dni string
	var number int
	fmt.Sscanf(betString, "AGENCY=%s,FIRST_NAME=%s,LAST_NAME=%s,NUMBER=%d,BIRTH_DATE=%s,DNI=%s", &agency, &name, &surname, &number, &birthDate, &dni)
	return &Bet{agency, name, surname, number, birthDate, dni}
}

// NewBet Initializes a new Bet entity
func NewBet(agency, name, surname, birthDate, dni string, number int) *Bet {
	bet := &Bet{
		agency:     agency,
		first_name: name,
		last_name:  surname,
		number:     number,
		birthDate:  birthDate,
		dni:        dni,
	}
	return bet
}

// BetsInBatches Entity that encapsulates a batch of bets
type BetsInBatches struct {
	bets []*Bet
}

// CreateBetsInBatches divides the bets into batches that don't exceed the max batch size
// and returns a slice of BetsInBatches.
// It also takes into account the maximum packet size that can be sent through the network
// and creates a new batch if the current batch exceeds it.
func CreateBetsInBatches(bets []*Bet, maxBatchSize int) []*BetsInBatches {
	var batches []*BetsInBatches
	var currentBatch []*Bet
	var currentBatchSize int // number of bytes in the current batch. It doesn't take into account the bets delimiters

	for _, bet := range bets {
		serializedBet := bet.Serialize()
		betSize := len(serializedBet) // number of bytes in the serialized bet. It doesn't include the message delimiter

		betsAmount := len(currentBatch)

		// Since the batch sent to the server will be serialized as "bet1;bet2;...;betN\n", which means that
		// there will be N-1 semicolons and 1 newline character, then
		// currentBatchSize + betSize + 1 (delimiter \n) + (betsAmount - 1 (delimiters ;))
		// currentBatchSize + betSize + betsAmount
		totalBytesBatch := currentBatchSize + betSize + betsAmount

		if totalBytesBatch > MAX_PACKET_SIZE || len(currentBatch) == maxBatchSize {
			batches = append(batches, &BetsInBatches{currentBatch})
			currentBatch = []*Bet{bet}
			currentBatchSize = betSize
		} else {
			currentBatch = append(currentBatch, bet)
			currentBatchSize += betSize
		}
	}
	if len(currentBatch) > 0 {
		batches = append(batches, &BetsInBatches{currentBatch})
	}

	return batches
}

// SerializeBatch serializes a batch of bets into a string with the following format:
// bet1;bet2;...;betN
func (b *BetsInBatches) Serialize() string {
	betsSerialized := []string{}
	for _, bet := range b.bets {
		betsSerialized = append(betsSerialized, bet.Serialize())
	}
	return strings.Join(betsSerialized, BETS_DELIMITER)

}

// Size returns the number of bets in the batch
func (b *BetsInBatches) Size() int {
	return len(b.bets)
}
