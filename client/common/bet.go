package common

import (
	"fmt"
	"strings"
)

const MAX_PACKET_SIZE = 8192

// Bet Entity encapsulates information abount an specific bet
type Bet struct {
	agency     string
	first_name string
	last_name  string
	number     int
	birthDate  string
	dni        string
}

// Serialize Returns a string representation of the Bet entity
func (b *Bet) Serialize() string {
	return fmt.Sprintf("AGENCY=%s,FIRST_NAME=%s,LAST_NAME=%s,NUMBER=%d,BIRTH_DATE=%s,DNI=%s", b.agency, b.first_name, b.last_name, b.number, b.birthDate, b.dni)
}

// DeserializeBet Receives a string and returns a Bet entity
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

type BetsInBatches struct {
	bets []*Bet
}

// CreateBetsInBatches divides the bets into batches that don't exceed the max batch size
func CreateBetsInBatches(bets []*Bet, maxBatchSize int) []*BetsInBatches {
	var batches []*BetsInBatches
	var currentBatch []*Bet
	var currentBatchSize int

	for _, bet := range bets {
		serializedBet := bet.Serialize()
		betSize := len(serializedBet)

		if currentBatchSize+betSize+1 > MAX_PACKET_SIZE || len(currentBatch) == maxBatchSize {
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

// SerializeBatch serializes a batch of bets
func (b *BetsInBatches) Serialize() string {
	betsSerialized := []string{}
	for _, bet := range b.bets {
		betsSerialized = append(betsSerialized, bet.Serialize())
	}
	return strings.Join(betsSerialized, ";")

}

// Size returns the number of bets in the batch
func (b *BetsInBatches) Size() int {
	return len(b.bets)
}
