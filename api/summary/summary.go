package summary

import (
	"../coins"
	"../investments"
	"../investors"
	"../utils"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"net/http"
)

func Summary() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		_, per_page := utils.GetPagination(r.RequestURI)
		// This abomination goes here
		result := make(map[string]map[string]map[string]int)
		result["coins"] = make(map[string]map[string]int)
		result["coins"]["invested"] = make(map[string]int)
		result["coins"]["invested"]["coins"] = coins.CoinsInvestedReturn()
		result["coins"]["total"] = make(map[string]int)
		result["coins"]["total"]["coins"] = coins.CoinsTotalReturn()
		result["investments"] = make(map[string]map[string]int)
		result["investments"]["active"] = make(map[string]int)
		result["investments"]["active"]["investments"] = investments.InvestmentsActiveReturn()
		to_show, _ := json.Marshal(result)
		to_add := fmt.Sprintf(`,"investors": {"top": %s}}`, investors.InvestorsTopReturn(per_page))
		fmt.Fprintf(w, "%s", string(to_show[:len(to_show)-1])+to_add)
	}
}
