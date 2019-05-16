package investor

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

type investor struct {
	Id        int      `json:"id"`
	Name      string   `json:"name"`
	Balance   int64    `json:"balance"`
	Completed int      `json:"completed"`
	Broke     int      `json:"broke"`
	Badges    []string `json:"badges"`
	Firm      int      `json:"firm"`
	Firm_role string   `json:"firm_role"`
	NetWorth  int64    `json:"networth"`
	Rank      int64    `json:"rank"`
}

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
}

func Investor() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		params := mux.Vars(r)
		name, ok := params["name"]
		if !ok {
			log.Print("No name provided.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		// Check regexp
		re := regexp.MustCompile(`^[-_a-zA-Z0-9]+$`)
		if !re.Match([]byte(name)) {
			log.Print("Provided name does not pass regex.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		conn, err := sql.Open("mysql", utils.GetDB())
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer conn.Close()
		query := fmt.Sprintf("SELECT * FROM Investors WHERE name = '%s'", name)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		temp := investor{}
		var badges_temp string
		for rows.Next() {
			err := rows.Scan(
				&temp.Id,
				&temp.Name,
				&temp.Balance,
				&temp.Completed,
				&temp.Broke,
				&badges_temp,
				&temp.Firm,
				&temp.Firm_role,
			)
			if err != nil {
				log.Print(err)
				w.WriteHeader(http.StatusBadRequest)
				return
			}
			json.Unmarshal([]byte(badges_temp), &temp.Badges)
		}
		// Making it networth
		query_net := fmt.Sprintf("SELECT COALESCE(SUM(amount),0) FROM Investments WHERE name = '%s' AND done = 0", name)
		var active_coins int64
		err = conn.QueryRow(query_net).Scan(&active_coins)
		temp.NetWorth = temp.Balance + active_coins

		// Calculate the investor's rank
		query_rank := fmt.Sprintf(`
SELECT position FROM (
  SELECT ROW_NUMBER() OVER (ORDER BY networth DESC) AS position, name, networth FROM (
    SELECT
    Investors.name, SUM(COALESCE(Investments.amount, 0)) + Investors.balance AS networth
    FROM Investors 
    LEFT OUTER JOIN (SELECT * FROM Investments WHERE done = 0) 
    AS Investments ON Investments.name = Investors.name 
    GROUP BY Investors.id
    ORDER BY networth DESC
  )sub
)sub1 WHERE name = '%s';
`, temp.Name)

		var rank int64
		err = conn.QueryRow(query_rank).Scan(&rank)

		temp.Rank = rank

		result, _ := json.Marshal(temp)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}

func InvestorInvestments() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		from, to := utils.GetTimeframes(r.RequestURI)
		page, per_page := utils.GetPagination(r.RequestURI)
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
		query := fmt.Sprintf(`
SELECT id, post, upvotes, comment, 
name, amount, time, done, response, 
COALESCE(final_upvotes, -1), success, profit 
FROM Investments 
WHERE name = '%s' AND time > %d AND time < %d 
ORDER BY time DESC 
LIMIT %d OFFSET %d`, name, from, to, per_page, per_page*page)
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
}

func InvestorInvestmentsActive() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		from, to := utils.GetTimeframes(r.RequestURI)
		page, per_page := utils.GetPagination(r.RequestURI)
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
		query := fmt.Sprintf(`
SELECT id, post, upvotes, comment, 
name, amount, time, done, response, 
COALESCE(final_upvotes, -1), success, profit 
FROM Investments 
WHERE name = '%s' AND done = 0 AND time > %d AND time < %d 
ORDER BY time DESC 
LIMIT %d OFFSET %d`, name, from, to, per_page, per_page*page)
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
}
