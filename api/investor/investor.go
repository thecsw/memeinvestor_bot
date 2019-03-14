package investor

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

type investor struct {
	Id        string `json:"id,omitempty"`
	Name      string `json:"name,omitempty"`
	Balance   int64  `json:"balance,omitempty"`
	Completed int    `json:"completed,omitempty"`
	Broke     int    `json:"broke,omitempty"`
	Badges    string `json:"badges,omitempty"`
	Firm      int    `json:"firm,omitempty"`
	Firm_role string `json:"firm_role,omitempty"`
}

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

func Investor(w http.ResponseWriter, r *http.Request) {
	log.Print(r.RequestURI)
	params := mux.Vars(r)
	name, ok := params["name"]
	if !ok {
		log.Print("No name provided.")
		return
	}
	// Check regexp
	re := regexp.MustCompile(`^[-_a-zA-Z0-9]+$`)
	if !re.Match([]byte(name)) {
		log.Print("Provided name does not pass regex.")
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()
	query := fmt.Sprintf("SELECT * FROM Investors WHERE name = '%s'", name)
	rows, err := conn.Query(query)
	if err != nil {
		log.Print(err)
		return
	}
	defer rows.Close()
	temp := investor{}
	for rows.Next() {
		err := rows.Scan(
			&temp.Id,
			&temp.Name,
			&temp.Balance,
			&temp.Completed,
			&temp.Broke,
			&temp.Badges,
			&temp.Firm,
			&temp.Firm_role,
		)
		if err != nil {
			log.Print(err)
		}
	}
	// Making it networth
	query_net := fmt.Sprintf("SELECT COALESCE(SUM(amount),0) FROM Investments WHERE name = '%s' AND done = 0", name)
	var active_coins int64
	err = conn.QueryRow(query_net).Scan(&active_coins)
	temp.Balance += active_coins
	result, _ := json.Marshal(temp)
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", string(result))
}

func InvestorInvestments(w http.ResponseWriter, r *http.Request) {
	log.Print(r.RequestURI)
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
	params := mux.Vars(r)
	name, ok := params["name"]
	if !ok {
		log.Print("No name provided.")
		return
	}
	// Check regexp
	re := regexp.MustCompile(`^[-_a-zA-Z0-9]+$`)
	if !re.Match([]byte(name)) {
		log.Print("Provided name does not pass regex.")
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()
	// Making it networth
	query := fmt.Sprintf("SELECT id, post, upvotes, comment, name, amount, time, done, response, COALESCE(final_upvotes, -1), success, profit FROM Investments WHERE name = '%s' AND time > %d AND time < %d ORDER BY time DESC LIMIT %d OFFSET %d", name, from, to, per_page, per_page*page)
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
			return
		}
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", string(result))
}

func InvestorInvestmentsActive(w http.ResponseWriter, r *http.Request) {
	log.Print(r.RequestURI)
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
	params := mux.Vars(r)
	name, ok := params["name"]
	if !ok {
		log.Print("No name provided.")
		return
	}
	// Check regexp
	re := regexp.MustCompile(`^[-_a-zA-Z0-9]+$`)
	if !re.Match([]byte(name)) {
		log.Print("Provided name does not pass regex.")
		return
	}
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()
	query := fmt.Sprintf("SELECT id, post, upvotes, comment, name, amount, time, done, response, COALESCE(final_upvotes, -1), success, profit FROM Investments WHERE name = '%s' AND done = 0 AND time > %d AND time < %d ORDER BY time DESC LIMIT %d OFFSET %d", name, from, to, per_page, per_page*page)
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
			return
		}
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", string(result))
}
