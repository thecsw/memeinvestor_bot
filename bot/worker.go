package main

import (
	"fmt"
	"time"

	"errors"

	"../utils"
	"github.com/thecsw/mira"
)

const (
	NeedAccount = "You don't have an account with us to perform the action. Please invoke '!create' to create an account!"
)

func worker(r *mira.Reddit, comment mira.CommentListingDataChildren) {
	start := time.Now()
	text := comment.GetBody()
	exists, _ := utils.UserExists(comment.GetAuthor())
	switch {
	// No account required
	case utils.RegMatch(`!template (.+)`, text):
		process(start, comment, template(r, comment))
		return
	case utils.RegMatch(`!create`, text):
		process(start, comment, create(r, comment))
		return

		// Check if user has an account
	case !exists:
		process(start, comment, errors.New("Account required."))
		r.Reply(comment.GetId(), NeedAccount)
		return

		// Account required
	case utils.RegMatch(`!balance`, text):
		process(start, comment, balance(r, comment))
		return
	}
}

func process(start time.Time, comment mira.CommentListingDataChildren, status error) {
	finish := time.Now()
	// Output the worker log
	fmt.Printf("%v [%v] %v %v %v \"%v\" %v \"%v\"\n",
		"bot",
		start.Format(time.RFC1123),
		comment.GetId(),
		comment.GetAuthor(),
		comment.GetSubreddit(),
		comment.GetBody(),
		finish.Sub(start),
		status,
	)
}
