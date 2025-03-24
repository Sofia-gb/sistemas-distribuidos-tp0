package common

import "strings"

// Winners encapsulates the winners' DNIs.
type Winners struct {
	dnis []string
}

// GetWinners creates a Winners struct that contains the winners' DNIs.
func GetWinners(winnersData string) Winners {
	var dnis []string

	parts := strings.SplitN(winnersData, ":", 2)
	if len(parts) == 2 {
		dnis = strings.Split(parts[1], ",")
	}
	return Winners{dnis}
}

// Size returns the number of winners.
func (w *Winners) Size() int {
	return len(w.dnis)
}
