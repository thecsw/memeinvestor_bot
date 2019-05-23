package main

import (
	"github.com/thecsw/mira"
)

func balance(r *mira.Reddit, comment mira.CommentListingDataChildren) error {
	r.Reply(comment.GetId(), "You are rich!")
	return nil
}
