package main

import (
	"./coins"
	"./investments"
	"./investor"
	"./investors"
	"./utils"
	"./summary"
	"fmt"
	"github.com/gorilla/mux"
	"log"
	"net/http"
)

func HelloThere(w http.ResponseWriter, r *http.Request) {
     	for _, v := range utils.GetDocumentation() {
	      	fmt.Fprintf(w, "%s\n", v)   
	}
	w.WriteHeader(http.StatusOK)
}

func main() {
	log.SetPrefix("Exception caught: ")
	r := mux.NewRouter()
	r.HandleFunc("/", HelloThere).Methods("GET")
	r.HandleFunc("/summary", summary.Summary).Methods("GET")
	r.HandleFunc("/coins/invested", coins.CoinsInvested).Methods("GET")
	r.HandleFunc("/coins/total", coins.CoinsTotal).Methods("GET")
	r.HandleFunc("/investments", investments.Investments).Methods("GET")
	r.HandleFunc("/investments/active", investments.InvestmentsActive).Methods("GET")
	r.HandleFunc("/investments/total", investments.InvestmentsTotal).Methods("GET")
	r.HandleFunc("/investments/amount", investments.InvestmentsAmount).Methods("GET")
	r.HandleFunc("/investments/post/{post}", investments.InvestmentsPost).Methods("GET")
	r.HandleFunc("/investor/{name}", investor.Investor).Methods("GET")
	r.HandleFunc("/investor/{name}/investments", investor.InvestorInvestments).Methods("GET")
	r.HandleFunc("/investor/{name}/active", investor.InvestorInvestmentsActive).Methods("GET")
	r.HandleFunc("/investors/top", investors.InvestorsTop).Methods("GET")
	log.Fatal(http.ListenAndServe(":5000", r))
}
