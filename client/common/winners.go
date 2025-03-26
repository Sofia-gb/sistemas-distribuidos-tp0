package common

import "strings"

const WINNERS_DELIMITER = ":"
const DNIS_DELIMITER = ","

// Winners encapsulates the winners' DNIs.
type Winners struct {
	dnis []string
}

// GetWinners creates a Winners struct that contains the winners' DNIs.
func GetWinners(winnersData string) Winners {
	var dnis []string

	parts := strings.SplitN(winnersData, WINNERS_DELIMITER, 2)
	if len(parts) == 2 {
		dnis_data := strings.TrimSpace(parts[1])
		if dnis_data != "" {
			dnis = strings.Split(parts[1], DNIS_DELIMITER)
		}
	}
	return Winners{dnis}
}

// Size returns the number of winners.
func (w *Winners) Size() int {
	return len(w.dnis)
}
