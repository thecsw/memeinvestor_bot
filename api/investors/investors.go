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
	Id        string `json:"id,omitempty"`
	Name      string `json:"name,omitempty"`
	Balance   int64  `json:"balance,omitempty"`
	Completed int    `json:"completed,omitempty"`
	Broke     int    `json:"broke,omitempty"`
	Badges    string `json:"badges,omitempty"`
	Firm      int    `json:"firm,omitempty"`
	Firm_role string `json:"firm_role,omitempty"`
	NetWorth  int64  `json:"networth,omitempty"`
}

func InvestorsTop(w http.ResponseWriter, r *http.Request) {
	log.Print(r.RequestURI)

	page, per_page, err := utils.GetPagination(r.RequestURI)
	if err != nil {
		log.Print(err)
		return
	}

	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()

	query := fmt.Sprintf("SELECT Investors.id, Investors.name,  Investors.balance, Investors.completed, Investors.broke, Investors.badges, Investors.firm, Investors.firm_role, SUM(COALESCE(Investments.amount, 0)) + Investors.balance AS net_worth FROM Investors LEFT OUTER JOIN (SELECT * FROM Investments WHERE done = 0) AS Investments ON Investments.name = Investors.name GROUP BY Investors.id ORDER BY net_worth DESC LIMIT %d OFFSET %d;", per_page, per_page * page)
	fmt.Println(query)
	rows, err := conn.Query(query)
	if err != nil {
		log.Print(err)
		return
	}
	defer rows.Close()

	wrapper := make([]investor, 0, per_page)
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
			&temp.NetWorth,
		)
		if err != nil {
			log.Print(err)
		}
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", string(result))
}

func InvestorsTopReturn(top int) string {
	conn, err := sql.Open("mysql", utils.GetDB())
	if err != nil {
		log.Print(err)
	}
	defer conn.Close()

	query := fmt.Sprintf("SELECT Investors.id, Investors.name,  Investors.balance, Investors.completed, Investors.broke, Investors.badges, Investors.firm, Investors.firm_role, SUM(COALESCE(Investments.amount, 0)) + Investors.balance AS net_worth FROM Investors LEFT OUTER JOIN (SELECT * FROM Investments WHERE done = 0) AS Investments ON Investments.name = Investors.name GROUP BY Investors.id ORDER BY net_worth DESC LIMIT %d;", top)
	fmt.Println(query)
	rows, err := conn.Query(query)
	if err != nil {
		log.Print(err)
		return ""
	}
	defer rows.Close()

	wrapper := make([]investor, 0, top)
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
			&temp.NetWorth,
		)
		if err != nil {
			log.Print(err)
		}
		wrapper = append(wrapper, temp)
	}
	result, _ := json.Marshal(wrapper)
	return string(result)
}
