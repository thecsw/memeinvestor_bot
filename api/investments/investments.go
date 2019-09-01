package investments

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"

	"../utils"
	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
)

type investment struct {
	Id            int    `json:"id"`
	Post          string `json:"post"`
	Upvotes       int    `json:"upvotes"`
	Comment       string `json:"comment"`
	Name          string `json:"name"`
	Amount        int64  `json:"amount"`
	Time          int    `json:"time"`
	Done          bool   `json:"done"`
	Response      string `json:"response"`
	Final_upvotes int    `json:"final_upvotes"`
	Success       bool   `json:"success"`
	Profit        int64  `json:"profit"`
	Firm_tax      int64  `json:"firm_tax"`
}

// Investments on time
func Investments() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		from, to := utils.GetTimeframes(r.RequestURI)
		page, per_page := utils.GetPagination(r.RequestURI)
		conn, err := sql.Open("mysql", utils.GetDB())
		defer conn.Close()
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		query := fmt.Sprintf(`
SELECT id, post, upvotes, comment, 
name, amount, time, done, response, 
COALESCE(final_upvotes, -1), success, profit, COALESCE(firm_tax, -1)
FROM Investments WHERE time > %d AND time < %d
ORDER BY time DESC 
LIMIT %d OFFSET %d;`, from, to, per_page, per_page*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
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
				&temp.Firm_tax,
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
}

// Active investments
func InvestmentsActive() func(w http.ResponseWriter, r *http.Request) {
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
		query := "SELECT COUNT(1) FROM Investments WHERE done = 0;"
		err = conn.QueryRow(query).Scan(&number)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		wrapper["investments"] = number
		result, _ := json.Marshal(wrapper)
		fmt.Fprintf(w, "%s", string(result))
	}
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
func InvestmentsAmount() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		from, to := utils.GetTimeframes(r.RequestURI)
		conn, err := sql.Open("mysql", utils.GetDB())
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer conn.Close()

		var number int64
		wrapper := make(map[string]int64)
		query := fmt.Sprintf("SELECT COALESCE(SUM(amount),0) FROM Investments WHERE time > %d AND time < %d;", from, to)
		err = conn.QueryRow(query).Scan(&number)
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

// Total
func InvestmentsTotal() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		log.Print(r.RequestURI)
		from, to := utils.GetTimeframes(r.RequestURI)
		conn, err := sql.Open("mysql", utils.GetDB())
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer conn.Close()

		var number int64
		wrapper := make(map[string]int64)
		query := fmt.Sprintf("SELECT COUNT(1) FROM Investments WHERE time > %d AND time < %d;", from, to)
		err = conn.QueryRow(query).Scan(&number)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		wrapper["investments"] = number
		result, _ := json.Marshal(wrapper)
		fmt.Fprintf(w, "%s", string(result))
	}
}

// Post
func InvestmentsPost() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		params := mux.Vars(r)
		post, ok := params["post"]
		if !ok {
			log.Print("No post provided.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		// Check regexp
		re := regexp.MustCompile(`^[a-z0-9]{6}$`)
		if !re.Match([]byte(post)) {
			log.Print("Provided post does not pass regex.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		from, to := utils.GetTimeframes(r.RequestURI)
		page, per_page := utils.GetPagination(r.RequestURI)
		conn, err := sql.Open("mysql", utils.GetDB())
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer conn.Close()
		query := fmt.Sprintf(`
SELECT id, post, upvotes, comment, 
name, amount, time, done, response, 
COALESCE(final_upvotes, -1), success, profit, COALESCE(firm_tax, -1)
FROM Investments 
WHERE time > %d AND time < %d AND post = '%s' 
ORDER BY time DESC 
LIMIT %d OFFSET %d;`, from, to, post, per_page, per_page*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
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
				&temp.Firm_tax,
			)
			if err != nil {
				log.Print(err)
				w.WriteHeader(http.StatusBadRequest)
				return
			}
			wrapper = append(wrapper, temp)
		}
		result, _ := json.Marshal(wrapper)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}
