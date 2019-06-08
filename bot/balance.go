package main

import (
	"fmt"

	"../models"
	"github.com/thecsw/mira"
)

func balance(r *mira.Reddit, comment mira.Comment) error {
	author := comment.GetAuthor()
	investor, err := models.Investors.GetUser(author)
	if err != nil {
		return err
	}
	message := fmt.Sprintf("Your balance is %d Mc",
		investor.Balance,
	)
	r.Reply(comment.GetId(), message)
	return nil
}
