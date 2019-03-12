package summary

import (
	"../coins"
	"../investments"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"net/http"
)

func Summary(w http.ResponseWriter, r *http.Request) {
	result := make(map[string]map[string]int)
	result["coins"]["invested"] = coins.CoinsInvestedReturn()
	result["coins"]["total"] = coins.CoinsTotalReturn()
	result["investments"]["active"] = investments.InvestmentsActiveReturn()
	result["investments"]["total"] = -1
	to_show, _ := json.Marshal(result)
	fmt.Fprintf(w, "%s", string(to_show))	
}
