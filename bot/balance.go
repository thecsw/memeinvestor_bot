package main

import (
	"database/sql"
	"fmt"

	"github.com/thecsw/memeinvestor_bot/utils"
	_ "github.com/lib/pq"
	"github.com/thecsw/mira"
)

func balance(r *mira.Reddit, comment mira.CommentListingDataChildren) error {
	db, err := sql.Open("postgres", utils.GetDB())
	if err != nil {
		return err
	}
	bal := 0
	statement := "select balance from investor where name = $1;"
	err = db.QueryRow(statement, comment.GetAuthor()).Scan(&bal)
	if err != nil {
		return err
	}
	message := fmt.Sprintf("Your balance is %d Mc",
		bal,
	)
	r.Reply(comment.GetId(), message)
	return nil
}
