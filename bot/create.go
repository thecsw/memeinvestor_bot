package main

import (
	"../commands"
	"../commands/wrap"
	"github.com/thecsw/mira"
)

func create(r *mira.Reddit, comment mira.Comment) error {
	err := commands.CreateInvestor(wrap.CreateInvestorWrap{
		Name:   comment.GetAuthor(),
		Source: "reddit",
	})
	if err != nil {
		if err.Error() == "Account already exists." {
			r.Reply(comment.GetId(), err.Error())
		}
		return err
	}
	message := "Account successfully created!"
	r.Reply(comment.GetId(), message)
	return nil
}
