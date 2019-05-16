package main

import (
	"github.com/thecsw/mira"
)

func main() {
	r, _ := mira.Init(mira.ReadCredsFromFile("login.conf"))
	c, _ := r.StreamCommentReplies()
	for {
		go worker(r, <-c)
	}
}
