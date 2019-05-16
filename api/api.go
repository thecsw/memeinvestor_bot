package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	"./coins"
	"./firm"
	"./firms"
	"./investments"
	"./investor"
	"./investors"
	"./summary"
	"github.com/gorilla/mux"
)

func HelloThere() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "%s\n", "Welcome to u/MemeInvestor_bot official RESTful API!\n")
		fmt.Fprintf(w, "%s\n", "Please see https://github.com/MemeInvestor/memeinvestor_bot/wiki/API-Documentation for more information!")
		w.WriteHeader(http.StatusOK)
	}
}

func main() {
	log.SetPrefix("Exception caught: ")
	r := mux.NewRouter()
	r.HandleFunc("/", HelloThere()).Methods("GET")
	r.HandleFunc("/summary", summary.Summary()).Methods("GET")
	r.HandleFunc("/coins/invested", coins.CoinsInvested()).Methods("GET")
	r.HandleFunc("/coins/total", coins.CoinsTotal()).Methods("GET")
	r.HandleFunc("/investments", investments.Investments()).Methods("GET")
	r.HandleFunc("/investments/active", investments.InvestmentsActive()).Methods("GET")
	r.HandleFunc("/investments/total", investments.InvestmentsTotal()).Methods("GET")
	r.HandleFunc("/investments/amount", investments.InvestmentsAmount()).Methods("GET")
	r.HandleFunc("/investments/post/{post}", investments.InvestmentsPost()).Methods("GET")
	r.HandleFunc("/investor/{name}", investor.Investor()).Methods("GET")
	r.HandleFunc("/investor/{name}/investments", investor.InvestorInvestments()).Methods("GET")
	r.HandleFunc("/investor/{name}/active", investor.InvestorInvestmentsActive()).Methods("GET")
	r.HandleFunc("/investors/top", investors.InvestorsTop()).Methods("GET")
	r.HandleFunc("/investors/last24", investors.InvestorsLast24()).Methods("GET")
	r.HandleFunc("/firms/top", firms.FirmsTop()).Methods("GET")
	r.HandleFunc("/firm/{id}", firm.Firm()).Methods("GET")
	r.HandleFunc("/firm/{id}/members", firm.FirmMembers()).Methods("GET")
	r.HandleFunc("/firm/{id}/members/top", firm.FirmMembersTop()).Methods("GET")
	srv := &http.Server{
		Handler: r,
		Addr:    ":5000",
		// Good practice: enforce timeouts for servers you create!
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}
	// Let it run
	go func() {
		if err := srv.ListenAndServe(); err != nil {
			log.Println(err)
		}
	}()
	c := make(chan os.Signal, 1)
	// We'll accept graceful shutdowns when quit via SIGINT (Ctrl+C)
	// SIGKILL, SIGQUIT or SIGTERM (Ctrl+/) will not be caught.
	signal.Notify(c, os.Interrupt)
	// Block until we receive our signal.
	<-c
	log.Println("shutting down")
	os.Exit(0)
}
