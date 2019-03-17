package coins

import (
	"../utils"
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"log"
	"net/http"
)

// Coins invested
func CoinsInvested() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		conn, err := sql.Open("mysql", utils.GetDB())
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer conn.Close()
		var number int
		wrapper := make(map[string]int)
		err = conn.QueryRow("SELECT COALESCE(SUM(amount),0) FROM Investments WHERE done = 0;").Scan(&number)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		wrapper["coins"] = number
		result, _ := json.Marshal(wrapper)
		fmt.Fprintf(w, "%s", string(result))
	}
}
func CoinsInvestedReturn() int {
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
		return -1
	}
	defer conn.Close()
	var number int
	err = conn.QueryRow("SELECT COALESCE(SUM(amount),0) FROM Investments WHERE done = 0;").Scan(&number)
	if err != nil {
		log.Print(err)
		return -1
	}
	return number
}

func CoinsTotal() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		conn, err := sql.Open("mysql", utils.GetDB())
		if err != nil {
			log.Print(err)
			return
		}
		defer conn.Close()

		var number int
		wrapper := make(map[string]int)
		err = conn.QueryRow("SELECT COALESCE(SUM(balance),0) FROM Investors;").Scan(&number)
		if err != nil {
			log.Print(err)
			return
		}
		wrapper["coins"] = number
		result, _ := json.Marshal(wrapper)
		fmt.Fprintf(w, "%s", string(result))
	}
}

func CoinsTotalReturn() int {
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
		return -1
	}
	defer conn.Close()

	var number int
	err = conn.QueryRow("SELECT COALESCE(SUM(balance),0) FROM Investors;").Scan(&number)
	return number
}
