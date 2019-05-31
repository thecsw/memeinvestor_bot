package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Printf("Sleeping for 10 seconds until database is online... ")
	time.Sleep(10 * time.Second)
	fmt.Printf("DONE!\n")
	fmt.Printf("Creating Investor... ")
	CreateInvestor()
	fmt.Printf("DONE!\n")
}
