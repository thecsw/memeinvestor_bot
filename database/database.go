package main

import (
	"fmt"

	"../utils"
)

func main() {
	// Waiting for the database to turn on
	fmt.Printf("Waiting for the database to respond... ")
	utils.WaitForDB()
	fmt.Printf("DONE\n")

	// Investor
	fmt.Printf("Creating Investor... ")
	InitInvestor()
	fmt.Printf("DONE\n")

	// Finishing statement
	fmt.Println("My work is done here.")
}
