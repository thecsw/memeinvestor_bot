package utils

import (
	"fmt"
	"os"
	"regexp"
)

func GetDB() string {
	return fmt.Sprintf("user=%s password=%s dbname=%s host=%s port=%s sslmode=disable",
		os.Getenv("POSTGRES_USER"),
		os.Getenv("POSTGRES_PASSWORD"),
		os.Getenv("POSTGRES_DB"),
		os.Getenv("POSTGRES_HOST"),
		os.Getenv("POSTGRES_PORT"),
	)
}

func GetTestDB() string {
	return "user=test password=pass dbname=db host=localhost port=9123 sslmode=disable"
}

func RegMatch(pattern, text string) bool {
	tmp, _ := regexp.Match(pattern, []byte(text))
	return tmp
}
