package utils

import (
	"database/sql"
	"fmt"
	"os"
	"regexp"
	"time"

	_ "github.com/lib/pq"
)

func GetDB() string {
	return fmt.Sprintf("user=%s password =%s dbname=%s host=%s port=%s sslmode=disable",
		os.Getenv("POSTGRES_USER"),
		os.Getenv("POSTGRES_PASSWORD"),
		os.Getenv("POSTGRES_DB"),
		os.Getenv("POSTGRES_HOST"),
		os.Getenv("POSTGRES_PORT"),
	)
}

func UserExists(author string) (bool, error) {
	db, err := sql.Open("postgres", GetDB())
	if err != nil {
		return false, err
	}
	num := 0
	statement := "select count(1) from investor where name=$1;"
	db.QueryRow(statement, author).Scan(&num)
	if num == 0 {
		return false, nil
	}
	return true, nil
}

func RegMatch(pattern, text string) bool {
	tmp, _ := regexp.Match(pattern, []byte(text))
	return tmp
}

func WaitForDB() {
	time.Sleep(30 * time.Second)
}
