package investments

import (
	"../creds"
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
//	"github.com/gorilla/mux"
	"log"
	"net/http"
)

type investment struct {
	Id            string `json:"id,omitempty"`
	Post          string `json:"post,omitempty"`
	Upvotes       int    `json:"upvotes,omitempty"`
	Comment       string `json:"comment,omitempty"`
	Name          string `json:"name,omitempty"`
	Amount        int64  `json:"amount,omitempty"`
	Time          int    `json:"time,omitempty"`
	Done          bool   `json:"done,omitempty"`
	Response      string `json:"response,omitempty"`
	Final_upvotes int    `json:"final_upvotes,omitempty"`
	Success       bool   `json:"success,omitempty"`
	Profit        int64  `json:"profit,omitempty"`
}

// Investments on time
func Investments(w http.ResponseWriter, r *http.Request) {
	// vars := mux.Vars(r)
	// limit := vars["limit"]
	// Opening a db connection
	conn, err := sql.Open("mysql", creds.GetDB())
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()
	
	rows, err := conn.Query("SELECT * FROM Investments")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()
	wrapper := make([]investment, 0, 100)
	temp := investment{}
	for rows.Next() {
		err := rows.Scan(
			&temp.Id,
			&temp.Post,
			&temp.Upvotes,
			&temp.Comment,
			&temp.Name,
			&temp.Amount,
			&temp.Time,
			&temp.Done,
			&temp.Response,
			&temp.Final_upvotes,
			&temp.Success,
			&temp.Profit,
		)
		if err != nil {
			log.Fatal(err)
		}
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", string(result))
}

// Active investments
func InvestmentsActive(w http.ResponseWriter, r *http.Request) {
	conn, err := sql.Open("mysql", creds.GetDB())
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	var number int
	wrapper := make(map[string]int)
	err = conn.QueryRow("select count(1) from Investments where done = 0;").Scan(&number)
	if err != nil {
		log.Fatal(err)
	}
	wrapper["investments"] = number
	result, _ := json.Marshal(wrapper)
	fmt.Fprintf(w, "%s", string(result))
}
