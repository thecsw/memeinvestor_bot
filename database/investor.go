package main

import (
	"database/sql"
	"fmt"

	"../mipq"
	"../models"
	_ "github.com/lib/pq"
)

func InitInvestor() {
	connStr := "user=test password='1234' dbname=db host=postgres port=5432 sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		fmt.Println(err)
		return
	}
	_, err = db.Exec(mipq.CreateTable(models.Investor{}))
	if err != nil {
		fmt.Println(err)
		return
	}
	db.Close()
}
