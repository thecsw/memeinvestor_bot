package main

import (
	"fmt"
	"time"
)

func main() {
	// Waiting for the database to turn on
	fmt.Printf("Sleeping for 30 seconds until database is online... ")
	time.Sleep(30 * time.Second)
	fmt.Printf("DONE!\n")
	// Investor
	fmt.Printf("Creating Investor... ")
	InitInvestor()
	fmt.Printf("DONE!\n")
	// Finishing statement
	fmt.Println("My work is done here.")
}
