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
	log.Print(r.RequestURI)
	from, to, err := utils.GetTimeframes(r.RequestURI)
	if err != nil {
		log.Print(err)
		fmt.Fprintf(w, "%s", err)
		return
	}
	page, per_page, err := utils.GetPagination(r.RequestURI)
	if err != nil {
		log.Print(err)
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
		return
	}
	query := fmt.Sprintf("SELECT id, post, upvotes, comment, name, amount, time, done, response, COALESCE(final_upvotes, -1), success, profit FROM Investments WHERE time > %d AND time < %d ORDER BY time DESC LIMIT %d OFFSET %d;", from, to, per_page, per_page*page)
	rows, err := conn.Query(query)
	if err != nil {
		log.Print(err)
		return
	}
	defer rows.Close()
	wrapper := make([]investment, 0, per_page)
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
			continue
		}
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", string(result))
}

// Active investments
func InvestmentsActive(w http.ResponseWriter, r *http.Request) {
	log.Print(r.RequestURI)
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
		return
	}
	defer conn.Close()

	var number int
	wrapper := make(map[string]int)
	query := "SELECT COUNT(1) FROM Investments WHERE done = 0;"
	err = conn.QueryRow(query).Scan(&number)
	if err != nil {
		log.Print(err)
	}
	wrapper["investments"] = number
	result, _ := json.Marshal(wrapper)
	fmt.Fprintf(w, "%s", string(result))
}

// Active investments with return
func InvestmentsActiveReturn() int {
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
		return -1
	}
	defer conn.Close()

	var number int
	query := "SELECT COUNT(1) FROM Investments WHERE done = 0;"
	err = conn.QueryRow(query).Scan(&number)
	if err != nil {
		log.Print(err)
	}
	return number
}

// Amount
func InvestmentsAmount(w http.ResponseWriter, r *http.Request) {
	log.Print(r.RequestURI)
	from, to, err := utils.GetTimeframes(r.RequestURI)
	if err != nil {
		log.Print(err)
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
		return
	}
	defer conn.Close()

	var number int64
	wrapper := make(map[string]int64)
	query := fmt.Sprintf("SELECT COALESCE(SUM(amount),0) FROM Investments WHERE time > %d AND time < %d;", from, to)
	err = conn.QueryRow(query).Scan(&number)
	if err != nil {
		log.Print(err)
	}
	wrapper["coins"] = number
	result, _ := json.Marshal(wrapper)
	fmt.Fprintf(w, "%s", string(result))
}

// Total
func InvestmentsTotal(w http.ResponseWriter, r *http.Request) {
	log.Print(r.RequestURI)
	from, to, err := utils.GetTimeframes(r.RequestURI)
	if err != nil {
		log.Print(err)
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
		return
	}
	defer conn.Close()

	var number int64
	wrapper := make(map[string]int64)
	query := fmt.Sprintf("SELECT COUNT(1) FROM Investments WHERE time > %d AND time < %d;", from, to)
	err = conn.QueryRow(query).Scan(&number)
	if err != nil {
		log.Print(err)
	}
	wrapper["investments"] = number
	result, _ := json.Marshal(wrapper)
	fmt.Fprintf(w, "%s", string(result))
}

// Post
func InvestmentsPost(w http.ResponseWriter, r *http.Request) {
	log.Print(r.RequestURI)
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
	page, per_page, err := utils.GetPagination(r.RequestURI)
	if err != nil {
		log.Print(err)
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()
	query := fmt.Sprintf("SELECT id, post, upvotes, comment, name, amount, time, done, response, COALESCE(final_upvotes, -1), success, profit FROM Investments WHERE time > %d AND time < %d AND post = '%s' ORDER BY time DESC LIMIT %d OFFSET %d;", from, to, post, per_page, per_page*page)
	rows, err := conn.Query(query)
	if err != nil {
		log.Print(err)
		return
	}
	defer rows.Close()
	wrapper := make([]investment, 0, per_page)
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
