package main

import (
	"database/sql"
	"fmt"

	"../mipq"
	"../models"
	"../utils"
	_ "github.com/lib/pq"
)

func InitInvestor() {
	db, err := sql.Open("postgres", utils.GetDB())
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
