package main

import (
	"database/sql"
	"fmt"
	_ "github.com/lib/pq"
	"github.com/thecsw/mira"
)

func balance(r *mira.Reddit, comment mira.CommentListingDataChildren) error {
	bal := 0
	connStr := "user=test password='1234' dbname=db host=postgres port=5432 sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return err
	}
	err = db.QueryRow(`
select balance from investors where name = $1;
`, comment.GetAuthor()).Scan(&bal)
	if err != nil {
		return err
	}
	r.Reply(comment.GetId(), fmt.Sprintf("Your balance is %s Mc", bal))
	return nil
}
