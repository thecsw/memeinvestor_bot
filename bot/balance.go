package main

import (
	"database/sql"
	"fmt"

	"../utils"
	_ "github.com/lib/pq"
	"github.com/thecsw/mira"
)

func balance(r *mira.Reddit, comment mira.CommentListingDataChildren) error {
	db, err := sql.Open("postgres", utils.GetDB())
	if err != nil {
		return err
	}
	bal := 0
	statement := "select balance from investors where name = $1;"
	err = db.QueryRow(statement, comment.GetAuthor()).Scan(&bal)
	if err != nil {
		return err
	}
	r.Reply(comment.GetId(), fmt.Sprintf("Your balance is %s Mc", bal))
	return nil
}
