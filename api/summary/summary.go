package summary

import (
	"encoding/json"
	"fmt"
	"net/http"

	"../coins"
	"../investments"
	"../investors"
	"../utils"
	// Register MySQL driver
	_ "github.com/go-sql-driver/mysql"
)

// Summary returns a summary of the meme markets
func Summary() func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		_, perPage := utils.GetPagination(r.RequestURI)
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
		toShow, _ := json.Marshal(result)
		toAdd := fmt.Sprintf(`,"investors": {"top": %s}}`, investors.TopNetWorth(perPage))
		fmt.Fprintf(w, "%s", string(toShow[:len(toShow)-1])+toAdd)
	}
}
