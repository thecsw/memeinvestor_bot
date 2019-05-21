package investors

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"../utils"
	_ "github.com/go-sql-driver/mysql"
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
}

type investorProfit struct {
	Name   string `json:"name"`
	Profit int64  `json:"profit"`
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
			return ""
		}
		json.Unmarshal([]byte(badges_temp), &temp.Badges)
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	return string(result)
}

func InvestorsLast24() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		page, per_page := utils.GetPagination(r.RequestURI)
		day_ago := time.Now().Unix() - 86400
		conn, err := sql.Open("mysql", utils.GetDB())
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer conn.Close()
		query := fmt.Sprintf(`
SELECT Investors.name, SUM(COALESCE(Investments.amount, 0))
AS profit FROM Investors 
LEFT OUTER JOIN (SELECT * FROM Investments WHERE done = 1 AND time > %d) 
AS Investments ON Investments.name = Investors.name 
GROUP BY Investors.id 
ORDER BY profit DESC 
LIMIT %d OFFSET %d;`, day_ago, per_page, per_page*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		wrapper := make([]investorProfit, 0, per_page)
		temp := investorProfit{}
		for rows.Next() {
			err := rows.Scan(
				&temp.Name,
				&temp.Profit,
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
