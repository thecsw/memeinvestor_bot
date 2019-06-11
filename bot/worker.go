package main

import (
	"errors"
	"fmt"
	"time"

	"../models"
	"../utils"
	"github.com/thecsw/mira"
)

const (
	NeedAccount = "You don't have an account with us to perform the action. Please invoke '!create' to create an account!"

	ErrNoAccount = "no account"
)

func worker(r *mira.Reddit, comment mira.Comment) {
	start := time.Now()
	body := comment.GetBody()
	author := comment.GetAuthor()
	commentId := comment.GetId()
	switch {
	case utils.RegMatch(`!template (.+)`, body):
		process(start, comment, template(r, comment))
		break
	case utils.RegMatch(`!create`, body):
		process(start, comment, create(r, comment))
		break
	case utils.RegMatch(`!top`, body):
		process(start, comment, top(r, comment))
		break
	case !models.Investors.Exists(author):
		process(start, comment, errors.New(ErrNoAccount))
		r.Reply(commentId, NeedAccount)
		break
	case utils.RegMatch(`!balance`, body):
		process(start, comment, balance(r, comment))
		break
	case utils.RegMatch(`!invest`, body):
		process(start, comment, invest(r, comment))
		break
	case utils.RegMatch(`!summary`, body):
		process(start, comment, summary(r, comment))
		break
	}
}

func process(start time.Time, comment mira.Comment, status error) {
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
