package firm

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"regexp"

	"../utils"
	// Registers MySQL driver
	_ "github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
)

type firm struct {
	ID         int    `json:"id"`
	Name       string `json:"name"`
	Balance    int64  `json:"balance"`
	Size       int    `json:"size"`
	Execs      int    `json:"execs"`
	Assocs     int    `json:"assocs"`
	Ceo        string `json:"ceo"`
	Coo        string `json:"coo"`
	Cfo        string `json:"cfo"`
	Tax        int    `json:"tax"`
	Level      int    `json:"level"`
	Private    bool   `json:"private"`
	LastPayout int    `json:"last_payout"`
	Rank       int64  `json:"rank"`
}

type investorNet struct {
	ID        int      `json:"id"`
	Name      string   `json:"name"`
	Balance   int64    `json:"balance"`
	Completed int      `json:"completed"`
	Broke     int      `json:"broke"`
	Badges    []string `json:"badges"`
	Firm      int      `json:"firm"`
	FirmRole  string   `json:"firm_role"`
	NetWorth  int64    `json:"networth"`
}

type investor struct {
	ID        int      `json:"id"`
	Name      string   `json:"name"`
	Balance   int64    `json:"balance"`
	Completed int      `json:"completed"`
	Broke     int      `json:"broke"`
	Badges    []string `json:"badges"`
	Firm      int      `json:"firm"`
	FirmRole  string   `json:"firm_role"`
	Rank      int64    `json:"rank"`
}

// Firm returns information about a firm
func Firm() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		params := mux.Vars(r)
		firmID, ok := params["id"]
		if !ok {
			log.Print("No ID provided.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		re := regexp.MustCompile(`^[0-9]+$`)
		if !re.Match([]byte(firmID)) {
			log.Print("Provided ID does not pass regex.")
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
		query := fmt.Sprintf(`
SELECT id, name, balance, size, execs, assocs, 
ceo, coo, cfo, tax, level, private, last_payout
FROM Firms
WHERE id = %s
ORDER BY balance DESC 
LIMIT 1;`, firmID)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		temp := firm{}
		for rows.Next() {
			err := rows.Scan(
				&temp.ID,
				&temp.Name,
				&temp.Balance,
				&temp.Size,
				&temp.Execs,
				&temp.Assocs,
				&temp.Ceo,
				&temp.Coo,
				&temp.Cfo,
				&temp.Tax,
				&temp.Level,
				&temp.Private,
				&temp.LastPayout,
			)
			if err != nil {
				log.Print(err)
				return
			}
		}

						// Calculate the firm's rank
		queryRank := fmt.Sprintf(`
SELECT position FROM (
  SELECT ROW_NUMBER() OVER (ORDER BY balance DESC) AS position, id, balance FROM (
    SELECT
    Firms.id, Firms.balance AS balance
    FROM Firms
    ORDER BY balance DESC
  )sub
)sub1 WHERE id = %d;
`, temp.ID)

		var rank int64
		err = conn.QueryRow(queryRank).Scan(&rank)

		temp.Rank = rank

		result, _ := json.Marshal(temp)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}

// Members returns the members of a firm
func Members() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		page, perPage := utils.GetPagination(r.RequestURI)
		params := mux.Vars(r)
		firmID, ok := params["id"]
		if !ok {
			log.Print("No ID provided.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		re := regexp.MustCompile(`^[0-9]+$`)
		if !re.Match([]byte(firmID)) {
			log.Print("Provided ID does not pass regex.")
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
		query := fmt.Sprintf(`
SELECT * FROM Investors WHERE firm = '%s'
LIMIT %d OFFSET %d`, firmID, perPage, perPage*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		wrapper := make([]investor, 0, perPage)
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
				return
			}
			json.Unmarshal([]byte(badgesTemp), &temp.Badges)
			wrapper = append(wrapper, temp)
		}

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

		result, _ := json.Marshal(wrapper)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}

// MembersTop returns the top members of a firm
func MembersTop() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		page, perPage := utils.GetPagination(r.RequestURI)
		params := mux.Vars(r)
		firmID, ok := params["id"]
		if !ok {
			log.Print("No ID provided.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		re := regexp.MustCompile(`^[0-9]+$`)
		if !re.Match([]byte(firmID)) {
			log.Print("Provided ID does not pass regex.")
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
		query := fmt.Sprintf(`
SELECT Investors.id, Investors.name,  Investors.balance, 
Investors.completed, Investors.broke, Investors.badges, 
Investors.firm, Investors.firm_role, 
SUM(COALESCE(Investments.amount, 0)) + Investors.balance 
AS net_worth
FROM Investors
LEFT OUTER JOIN (SELECT * FROM Investments WHERE done = 0) 
AS Investments ON Investments.name = Investors.name 
GROUP BY Investors.id
HAVING Investors.firm = %s
ORDER BY net_worth DESC
LIMIT %d OFFSET %d;`, firmID, perPage, perPage*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		wrapper := make([]investorNet, 0, perPage)
		temp := investorNet{}
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
				&temp.NetWorth,
			)
			if err != nil {
				log.Print(err)
				return
			}
			json.Unmarshal([]byte(badgesTemp), &temp.Badges)
			wrapper = append(wrapper, temp)
		}
		result, _ := json.Marshal(wrapper)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}
