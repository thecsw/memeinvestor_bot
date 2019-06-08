package investor

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"

	"../utils"
	// Register MySQL driver
	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
)

type investor struct {
	ID        int      `json:"id"`
	Name      string   `json:"name"`
	Balance   int64    `json:"balance"`
	Completed int      `json:"completed"`
	Broke     int      `json:"broke"`
	Badges    []string `json:"badges"`
	Firm      int      `json:"firm"`
	FirmRole  string   `json:"firm_role"`
	NetWorth  int64    `json:"networth"`
	Rank      int64    `json:"rank"`
}

type investment struct {
	ID            int    `json:"id"`
	Post          string `json:"post"`
	Upvotes       int    `json:"upvotes"`
	Comment       string `json:"comment"`
	Name          string `json:"name"`
	Amount        int64  `json:"amount"`
	Time          int    `json:"time"`
	Done          bool   `json:"done"`
	Response      string `json:"response"`
	FinalUpvotes  int    `json:"final_upvotes"`
	Success       bool   `json:"success"`
	Profit        int64  `json:"profit"`
	FirmTax       int64  `json:"firm_tax"`
}

// Investor returns investor object
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
		var badgesTemp string
		for rows.Next() {
			err := rows.Scan(
				&temp.ID,
				&temp.Name,
				&temp.Balance,
				&temp.Completed,
				&temp.Broke,
				&badgesTemp,
				&temp.Firm,
				&temp.FirmRole,
			)
			if err != nil {
				log.Print(err)
				w.WriteHeader(http.StatusBadRequest)
				return
			}
			json.Unmarshal([]byte(badgesTemp), &temp.Badges)
		}
		// Making it networth
		queryNet := fmt.Sprintf("SELECT COALESCE(SUM(amount),0) FROM Investments WHERE name = '%s' AND done = 0", name)
		var activeCoins int64
		err = conn.QueryRow(queryNet).Scan(&activeCoins)
		temp.NetWorth = temp.Balance + activeCoins

		// Calculate the investor's rank
		queryRank := fmt.Sprintf(`
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
		err = conn.QueryRow(queryRank).Scan(&rank)

		temp.Rank = rank

		result, _ := json.Marshal(temp)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}

// Investments returns an investor's investment history
func Investments() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		from, to := utils.GetTimeframes(r.RequestURI)
		page, perPage := utils.GetPagination(r.RequestURI)
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
COALESCE(final_upvotes, -1), success, profit, COALESCE(firm_tax, -1)
FROM Investments 
WHERE name = '%s' AND time > %d AND time < %d 
ORDER BY time DESC 
LIMIT %d OFFSET %d`, name, from, to, perPage, perPage*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			return
		}
		defer rows.Close()
		wrapper := make([]investment, 0, perPage)
		temp := investment{}
		for rows.Next() {
			err := rows.Scan(
				&temp.ID,
				&temp.Post,
				&temp.Upvotes,
				&temp.Comment,
				&temp.Name,
				&temp.Amount,
				&temp.Time,
				&temp.Done,
				&temp.Response,
				&temp.FinalUpvotes,
				&temp.Success,
				&temp.Profit,
				&temp.FirmTax,
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

// InvestmentsActive returns investor's active investments
func InvestmentsActive() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		from, to := utils.GetTimeframes(r.RequestURI)
		page, perPage := utils.GetPagination(r.RequestURI)
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
COALESCE(final_upvotes, -1), success, profit, COALESCE(firm_tax, -1)
FROM Investments 
WHERE name = '%s' AND done = 0 AND time > %d AND time < %d 
ORDER BY time DESC 
LIMIT %d OFFSET %d`, name, from, to, perPage, perPage*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			return
		}
		defer rows.Close()
		wrapper := make([]investment, 0, perPage)
		temp := investment{}
		for rows.Next() {
			err := rows.Scan(
				&temp.ID,
				&temp.Post,
				&temp.Upvotes,
				&temp.Comment,
				&temp.Name,
				&temp.Amount,
				&temp.Time,
				&temp.Done,
				&temp.Response,
				&temp.FinalUpvotes,
				&temp.Success,
				&temp.Profit,
				&temp.FirmTax,
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
