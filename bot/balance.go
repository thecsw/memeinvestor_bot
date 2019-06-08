package main

import (
	"fmt"

	"../commands"
	"../commands/wrap"
	"github.com/thecsw/mira"
)

func balance(r *mira.Reddit, comment mira.Comment) error {
	bal, err := commands.BalanceInvestor(wrap.BalanceInvestorWrap{
		Name: comment.GetAuthor(),
	})
	if err != nil {
		return err
	}
	message := fmt.Sprintf("Your balance is %d Mc",
		bal,
	)
	r.Reply(comment.GetId(), message)
	return nil
}
