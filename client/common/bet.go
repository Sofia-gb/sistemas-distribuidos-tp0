package common

import "fmt"

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

// NewBet Initializes a new Bet entity using the configuration received as parameter
func NewBet(config ClientConfig) *Bet {
	bet := &Bet{
		agency:     config.ID,
		first_name: config.Name,
		last_name:  config.Surname,
		number:     config.Bet,
		birthDate:  config.BirthDate,
		dni:        config.DNI,
	}
	return bet
}
