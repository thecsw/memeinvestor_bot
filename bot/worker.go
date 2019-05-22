package main

import (
	"fmt"
	"regexp"
	"time"

	"github.com/thecsw/mira"
)

func worker(r *mira.Reddit, comment mira.CommentListingDataChildren) {
	start := time.Now()
	// !balance
	balance_r, _ := regexp.Match(`!balance`, []byte(comment.GetBody()));
	if balance_r {
		balance(r, comment)
	}
	// !template (.+)
	template_r, _ := regexp.Match(`!template (.+)`, []byte(comment.GetBody()));
	if template_r {
		sub, _ := regexp.Compile(`!template (.+)`)
		template(r, comment, sub.FindStringSubmatch(comment.GetBody())[1])
	}

	finish := time.Now()
	source := `mira`
	// Output the worker log
	fmt.Printf("%v [%v] %v %v %v \"%v\" %v\n",
		source,
		start.Format(time.RFC1123),
		comment.GetId(),
		comment.GetAuthor(),
		comment.GetSubreddit(),
		comment.GetBody(),
		finish.Sub(start),
	)
}
