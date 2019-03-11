package coins

import (
	"../creds"
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"log"
	"net/http"
)

// Coins invested
func CoinsInvested(w http.ResponseWriter, r *http.Request) {
	conn, err := sql.Open("mysql", creds.GetDB())
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	var number int
	wrapper := make(map[string]int)
	err = conn.QueryRow("select sum(amount) from Investments where done = 0;").Scan(&number)
	if err != nil {
		log.Fatal(err)
	}
	wrapper["coins"] = number
	result, _ := json.Marshal(wrapper)
	fmt.Fprintf(w, "%s", string(result))
}

func CoinsTotal(w http.ResponseWriter, r *http.Request) {
	conn, err := sql.Open("mysql", creds.GetDB())
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	var number int
	wrapper := make(map[string]int)
	err = conn.QueryRow("select sum(balance) from Investors;").Scan(&number)
	if err != nil {
		log.Fatal(err)
	}
	wrapper["coins"] = number
	result, _ := json.Marshal(wrapper)
	fmt.Fprintf(w, "%s", string(result))
}
