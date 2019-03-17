package firm

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

type firm struct {
	Id         int    `json:"id"`
	Name       string `json:"name"`
	Balance    int64  `json:"balance"`
	Size       int    `json:"size"`
	Execs      int    `json:"execs"`
	Tax        int    `json:"tax"`
	Rank       int    `json:"rank"`
	Private    bool   `json:"private"`
	LastPayout int    `json:"last_payout"`
}

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
}

// Investments on time
func Firm() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		params := mux.Vars(r)
		firm_id, ok := params["id"]
		if !ok {
			log.Print("No ID provided.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		re := regexp.MustCompile(`^[0-9]+$`)
		if !re.Match([]byte(firm_id)) {
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
		query := fmt.Sprintf(`
SELECT id, name, balance, size, execs,
tax, rank, private, last_payout
FROM Firms
WHERE id = %s
ORDER BY balance DESC 
LIMIT 1;`, firm_id)
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
				&temp.Id,
				&temp.Name,
				&temp.Balance,
				&temp.Size,
				&temp.Execs,
				&temp.Tax,
				&temp.Rank,
				&temp.Private,
				&temp.LastPayout,
			)
			if err != nil {
				log.Print(err)
				return
			}
		}
		result, _ := json.Marshal(temp)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}

func FirmMembers() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		page, per_page := utils.GetPagination(r.RequestURI)
		params := mux.Vars(r)
		firm_id, ok := params["id"]
		if !ok {
			log.Print("No ID provided.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		re := regexp.MustCompile(`^[0-9]+$`)
		if !re.Match([]byte(firm_id)) {
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
		query := fmt.Sprintf(`
SELECT * FROM Investors WHERE firm = '%s'
LIMIT %d OFFSET %d`, firm_id, per_page, per_page*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		wrapper := make([]investor, 0, per_page)
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
				return
			}
			json.Unmarshal([]byte(badges_temp), &temp.Badges)
			wrapper = append(wrapper, temp)
		}
		result, _ := json.Marshal(wrapper)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}

func FirmMembersTop() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		page, per_page := utils.GetPagination(r.RequestURI)
		params := mux.Vars(r)
		firm_id, ok := params["id"]
		if !ok {
			log.Print("No ID provided.")
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		re := regexp.MustCompile(`^[0-9]+$`)
		if !re.Match([]byte(firm_id)) {
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
LIMIT %d OFFSET %d;`, firm_id, per_page, per_page*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		wrapper := make([]investor, 0, per_page)
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
				&temp.NetWorth,
			)
			if err != nil {
				log.Print(err)
				return
			}
			json.Unmarshal([]byte(badges_temp), &temp.Badges)
			wrapper = append(wrapper, temp)
		}
		result, _ := json.Marshal(wrapper)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}
