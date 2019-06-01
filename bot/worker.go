package main

import (
	"database/sql"
	"fmt"
	"regexp"
	"time"

	"../utils"
	_ "github.com/lib/pq"
	"github.com/thecsw/mira"
)

const (
	NeedAccount = "You don't have an account with us to perform the action. Please invoke '!create' to create an account!"
)

func worker(r *mira.Reddit, comment mira.CommentListingDataChildren) {
	start := time.Now()
	var status error = nil
	//
	// ### NO ACCOUNT NEEDED ###
	//

	// !template (.+)
	template_r, _ := regexp.Match(`!template (.+)`, []byte(comment.GetBody()))
	if template_r {
		status = template(r, comment)
	}
	// !create
	create_r, _ := regexp.Match(`!create`, []byte(comment.GetBody()))
	if create_r {
		status = create(r, comment)
	}

	//
	// ### ACCOUNT REQUIRED ###
	//

	// Check if the user has an account
	exists, _ := userExists(comment.GetAuthor())
	if !exists {
		r.Reply(comment.GetId(), NeedAccount)
		return
	}

	// !balance
	balance_r, _ := regexp.Match(`!balance`, []byte(comment.GetBody()))
	if balance_r {
		status = balance(r, comment)
	}
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

func userExists(author string) (bool, error) {
	db, err := sql.Open("postgres", utils.GetDB())
	if err != nil {
		return false, err
	}
	num := 0
	statement := "select count(1) from investor where name=$1"
	db.QueryRow(statement, author).Scan(&num)
	if num == 0 {
		return false, nil
	}
	return true, nil
}
