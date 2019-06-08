package main

import (
	"../models"
	"github.com/thecsw/mira"
)

func create(r *mira.Reddit, comment mira.CommentListingDataChildren) error {
	author := comment.GetAuthor()
	if models.Investors.Exists(comment.GetAuthor()) {
		r.Reply(comment.GetId(), "You already have an account!")
		return nil
	}
	err := models.Investors.Create(&models.Investor{
		Name:   author,
		Source: "reddit",
	})
	if err != nil {
		return err
	}
	message := "Account successfully created!"
	r.Reply(comment.GetId(), message)
	return nil
}
