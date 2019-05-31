package main

import (
	"fmt"
	"time"
)

func main() {
	// Waiting for the database to turn on
	fmt.Printf("Sleeping for 20 seconds until database is online... ")
	time.Sleep(20 * time.Second)
	fmt.Printf("DONE!\n")
	// Investor
	fmt.Printf("Creating Investor... ")
	InitInvestor()
	fmt.Printf("DONE!\n")
}
