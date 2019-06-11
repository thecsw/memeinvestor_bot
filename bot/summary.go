package main

import(
	"fmt"

	"../models"
	"github.com/thecsw/mira"
	"github.com/dustin/go-humanize"
)

const(
	SummaryMsg = "Your Summary:\n\nName: %s\n\nBalance: %s M\u00A2\n\nNet worth: %s M\u00A2\n\nFirm: %s"
)

func summary(r *mira.Reddit, comment mira.Comment) error{
	investor, err := models.Investors.GetUser(comment.GetAuthor())
	if err != nil{
		return err
	}

	// This should be constant, but Go does not allow for const maps
	firmRoles := map[string]string {
		"trader": 	"Floor Trader",
		"assoc": 	"Associate",
		"exec": 	"Executive",
		"coo": 		"COO",
		"cfo": 		"CFO",
		"ceo": 		"CEO",
	}

	// Display "--" if the user isn't in a firm
	firmStr := `--`
	if investor.Firm != 0 {
		firm, err := models.Firms.Get(investor.Firm)
		if err != nil{
			return err
		}
		firmStr = fmt.Sprintf("%s | %s", firm.Name, firmRoles[investor.FirmRole])
	}

	body := fmt.Sprintf(SummaryMsg, investor.Name, humanize.Comma(investor.Balance), humanize.Comma(investor.Networth), firmStr)

	r.Reply(comment.GetId(), body)

	return nil
}