package main

import (
	"fmt"
	"regexp"
	"time"

	"github.com/thecsw/mira"
)

func worker(r *mira.Reddit, comment mira.CommentListingDataChildren) {
	start := time.Now()
	var status error = nil
	// !balance
	balance_r, _ := regexp.Match(`!balance`, []byte(comment.GetBody()))
	if balance_r {
		status = balance(r, comment)
	}
	// !template (.+)
	template_r, _ := regexp.Match(`!template (.+)`, []byte(comment.GetBody()))
	if template_r {
		status = template(r, comment)
	}
	finish := time.Now()
	// Output the worker log
	fmt.Printf("%v [%v] %v %v %v \"%v\" %v \"%v\"\n",
		"submitter",
		start.Format(time.RFC1123),
		comment.GetId(),
		comment.GetAuthor(),
		comment.GetSubreddit(),
		comment.GetBody(),
		finish.Sub(start),
		status,
	)
}
