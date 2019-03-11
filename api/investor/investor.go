package investor

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

type investor struct {
	Id        string `json:"id,omitempty"`
	Name      string `json:"name,omitempty"`
	Balance   int64  `json:"balance,omitempty"`
	Completed int    `json:"completed,omitempty"`
	Broke     int    `json:"broke,omitempty"`
	Badges    string `json:"badges,omitempty"`
	Firm      int    `json:"firm,omitempty"`
	Firm_role string `json:"firm_role,omitempty"`
}

func Investor(w http.ResponseWriter, r *http.Request) {
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
	query := "SELECT * FROM Investors WHERE name = '" + name + "'"
	rows, err := conn.Query(query)
	if err != nil {
		log.Print(err)
		return
	}
	defer rows.Close()
	wrapper := make([]investor, 0, 100)
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
		)
		if err != nil {
			log.Print(err)
		}
		wrapper = append(wrapper, temp)
	}
	// Making it networth
	query_net := "select sum(amount) from Investments where name = '" + name + "' AND done = 0"
	var active_coins int64	
	err = conn.QueryRow(query_net).Scan(&active_coins)
	wrapper[0].Balance += active_coins
	result, _ := json.Marshal(wrapper[0])
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "%s", string(result))
}
