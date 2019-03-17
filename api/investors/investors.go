package investors

import (
	"../utils"
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"log"
	"net/http"
)

type investor struct {
	Id        int      `json:"id,omitempty"`
	Name      string   `json:"name,omitempty"`
	Balance   int64    `json:"balance,omitempty"`
	Completed int      `json:"completed,omitempty"`
	Broke     int      `json:"broke,omitempty"`
	Badges    []string `json:"badges,omitempty"`
	Firm      int      `json:"firm,omitempty"`
	Firm_role string   `json:"firm_role,omitempty"`
	NetWorth  int64    `json:"networth,omitempty"`
}

func InvestorsTop() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		page, per_page := utils.GetPagination(r.RequestURI)
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
ORDER BY net_worth DESC 
LIMIT %d OFFSET %d;`, per_page, per_page*page)
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
				w.WriteHeader(http.StatusBadRequest)
				continue
			}
			json.Unmarshal([]byte(badges_temp), &temp.Badges)
			wrapper = append(wrapper, temp)
		}
		result, _ := json.Marshal(wrapper)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "%s", string(result))
	}
}

func InvestorsTopReturn(top int) string {
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
		return ""
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
ORDER BY net_worth DESC 
LIMIT %d OFFSET 0;`, top)
	rows, err := conn.Query(query)
	if err != nil {
		log.Print(err)
		return ""
	}
	defer rows.Close()

	wrapper := make([]investor, 0, top)
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
			continue
		}
		json.Unmarshal([]byte(badges_temp), &temp.Badges)
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	return string(result)
}
