package firms

import (
	"../utils"
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"log"
	"net/http"
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

// Investments on time
func FirmsTop() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		page, per_page := utils.GetPagination(r.RequestURI)
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
ORDER BY balance DESC 
LIMIT %d OFFSET %d;`, per_page, per_page*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		wrapper := make([]firm, 0, per_page)
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
			wrapper = append(wrapper, temp)
		}
		result, _ := json.Marshal(wrapper)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}
