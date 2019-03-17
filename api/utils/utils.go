package utils

import (
	"fmt"
	"net/url"
	"os"
	"strconv"
)

func GetDB() string {
	// Follow the DSN (Data Source Name) PEAR DB format
	// For more details, consult the database driver:
	// https://github.com/go-sql-driver/mysql
	database := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s",
		os.Getenv("MYSQL_USER"),
		os.Getenv("MYSQL_PASSWORD"),
		os.Getenv("MYSQL_HOST"),
		os.Getenv("MYSQL_PORT"),
		os.Getenv("MYSQL_DATABASE"))
	return database
}

func GetTimeframes(path string) (int, int) {
	from_int, to_int := 0, 4294967295
	u, err := url.Parse(path)
	// Even if it fails, fallback to default values
	if err != nil {
		return from_int, to_int
	}
	queries := u.Query()
	if val, ok := queries["from"]; ok {
		from_int, _ = strconv.Atoi(val[0])
	}
	if val, ok := queries["to"]; ok {
		to_int, err = strconv.Atoi(val[0])
		if err != nil {
			to_int = 4294967295
		}
	}
	return from_int, to_int
}

func GetPagination(path string) (int, int) {
	// Pagination, default is the first page
	// with 100 elements max
	page_int, per_page_int := 0, 100
	u, err := url.Parse(path)
	if err != nil {
		return page_int, per_page_int
	}
	queries := u.Query()
	if val, ok := queries["page"]; ok {
		page_int, _ = strconv.Atoi(val[0])
		if page_int < 0 {
			page_int = 0
		}
	}
	if val, ok := queries["per_page"]; ok {
		per_page_int, err = strconv.Atoi(val[0])
		if err != nil || per_page_int > 100 || per_page_int < 0 {
			per_page_int = 100
		}
	}
	return page_int, per_page_int
}
