package investors

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"../utils"
	// Register MySQL driver
	_ "github.com/go-sql-driver/mysql"
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

type investorProfit struct {
	Name   string `json:"name"`
	Profit int64  `json:"profit"`
}

// Top returns the top investors of r/MemeEconomy
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
LIMIT %d OFFSET %d;`, perPage, perPage*page)
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
				&temp.NetWorth,
			)
			if err != nil {
				log.Print(err)
				w.WriteHeader(http.StatusBadRequest)
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

// Returns 
func TopNetWorth(top int) string {
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
			return ""
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
	return string(result)
}

// PastDay returns investors who've invested in the past day
func PastDay() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		page, perPage := utils.GetPagination(r.RequestURI)
		dayAgo := time.Now().Unix() - 86400
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
LIMIT %d OFFSET %d;`, dayAgo, perPage, perPage*page)
		rows, err := conn.Query(query)
		if err != nil {
			log.Print(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()
		wrapper := make([]investorProfit, 0, perPage)
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
