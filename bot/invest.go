package main

import (
	"fmt"

	"../models"
	"github.com/thecsw/mira"
)

func invest(r *mira.Reddit, comment mira.Comment) error {
	author := comment.GetAuthor()
	investor, err := models.Investors.GetUser(author)
	if err != nil {
		return err
	}
	investor.Balance -= 100
	models.Investors.Update(&investor)
	models.Investors.GoneBroke(author)
	models.Investors.GrantBadge(author, `tester`)
	arr := models.Investors.GetBrokeHistory(author)
	fmt.Println(len(arr))
	fmt.Println(arr)
	return nil
}
