package main

import (
	"./coins"
	"./investments"
	"fmt"
	"log"
	"net/http"
	"github.com/gorilla/mux"
)

func HelloThere(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello there! Welcome to u/MemeInvestor_bot api! Please see blablabla for details.")
}

func main() {
	log.SetPrefix("Exception caught: ")
	r := mux.NewRouter()
	r.HandleFunc("/", HelloThere).Methods("GET")
	r.HandleFunc("/coins/invested", coins.CoinsInvested).Methods("GET")
	r.HandleFunc("/coins/total", coins.CoinsTotal).Methods("GET")
	r.HandleFunc("/investments", investments.Investments).Methods("GET")
	r.HandleFunc("/investments/active", investments.InvestmentsActive).Methods("GET")
	r.HandleFunc("/investments/total", investments.InvestmentsTotal).Methods("GET")
	r.HandleFunc("/investments/amount", investments.InvestmentsAmount).Methods("GET")
	r.HandleFunc("/investments/post/{post}", investments.InvestmentsPost).Methods("GET")
	log.Fatal(http.ListenAndServe(":5000", r))
}
