package investments

import (
	"../utils"
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
	"log"
	"net/http"
	"regexp"
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
	from, to, err := utils.GetTimeframes(r.RequestURI)
	if err != nil {
		log.Print(err)
		return
	}
	// Opening a db connection
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
		return
	}
	defer conn.Close()
	query := "SELECT * FROM Investments WHERE time > " + from + " AND time < " + to
	rows, err := conn.Query(query)
	if err != nil {
		log.Print(err)
		return
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
			log.Print(err)
		}
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", string(result))
}

// Active investments
func InvestmentsActive(w http.ResponseWriter, r *http.Request) {
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()

	var number int
	wrapper := make(map[string]int)
	query := "select count(1) from Investments where done = 0;"
	err = conn.QueryRow(query).Scan(&number)
	if err != nil {
		log.Print(err)
	}
	wrapper["investments"] = number
	result, _ := json.Marshal(wrapper)
	fmt.Fprintf(w, "%s", string(result))
}

// Amount
func InvestmentsTotal(w http.ResponseWriter, r *http.Request) {
	from, to, err := utils.GetTimeframes(r.RequestURI)
	if err != nil {
		log.Print(err)
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()

	var number int64
	wrapper := make(map[string]int64)
	query := "select count(1) from Investments where time > " + from + " AND time < " + to
	err = conn.QueryRow(query).Scan(&number)
	if err != nil {
		log.Print(err)
	}
	wrapper["investments"] = number
	result, _ := json.Marshal(wrapper)
	fmt.Fprintf(w, "%s", string(result))
}

// Total
func InvestmentsAmount(w http.ResponseWriter, r *http.Request) {
	from, to, err := utils.GetTimeframes(r.RequestURI)
	if err != nil {
		log.Print(err)
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()

	var number int64
	wrapper := make(map[string]int64)
	query := "select sum(amount) from Investments where time > " + from + " AND time < " + to
	err = conn.QueryRow(query).Scan(&number)
	if err != nil {
		log.Print(err)
	}
	wrapper["coins"] = number
	result, _ := json.Marshal(wrapper)
	fmt.Fprintf(w, "%s", string(result))
}

// Post
func InvestmentsPost(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	post, ok := params["post"]
	if !ok {
		log.Print("No post provided.")
		return
	}
	// Check regexp
	re := regexp.MustCompile(`^[a-z0-9]{6}$`)
	if !re.Match([]byte(post)) {
		log.Print("Provided post does not pass regex.")
		return
	}
	from, to, err := utils.GetTimeframes(r.RequestURI)
	if err != nil {
		log.Print(err)
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()
	query := "SELECT * FROM Investments WHERE time > " + from + " AND time < " + to + " AND post = '" + post + "'"
	rows, err := conn.Query(query)
	if err != nil {
		log.Print(err)
		return
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
			log.Print(err)
		}
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", string(result))
}
