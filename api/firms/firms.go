package firms

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"../utils"
	// Register MySQL DB driver
	_ "github.com/go-sql-driver/mysql"
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

// Top gets the top firms
func Top() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		page, perPage := utils.GetPagination(r.RequestURI)
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
WHERE size > 0
ORDER BY balance DESC 
LIMIT %d OFFSET %d;`, perPage, perPage*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		wrapper := make([]firm, 0, perPage)
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
			wrapper = append(wrapper, temp)
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

		result, _ := json.Marshal(wrapper)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}
