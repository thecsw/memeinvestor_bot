package main

import (
	"regexp"

	"github.com/thecsw/mira"
)

func worker(r *mira.Reddit, comment mira.CommentListingDataChildren) {
	if balance_r, _ := regexp.Match(`!balance`, []byte(comment.GetBody())); balance_r {
		balance(r, comment)
	}
}
