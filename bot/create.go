package main

import (
	"database/sql"

	"errors"

	"../utils"
	_ "github.com/lib/pq"
	"github.com/thecsw/mira"
)

func create(r *mira.Reddit, comment mira.CommentListingDataChildren) error {
	author := comment.GetAuthor()
	statement := "insert into investor (name, source) values ($1, 'reddit');"
	db, err := sql.Open("postgres", utils.GetDB())
	if err != nil {
		return err
	}
	res, err := db.Exec(statement, author)
	if err != nil {
		return err
	}
	success, err := res.RowsAffected()
	if err != nil {
		return err
	}
	if success != 1 {
		return errors.New("Database error when adding new investor.")
	}
	message := "Account successfully created!"
	r.Reply(comment.GetId(), message)
	return nil
}
