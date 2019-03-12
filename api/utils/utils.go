package utils

import (
	"errors"
	"gitlab.com/golang-commonmark/markdown"
	"io/ioutil"
	"net/url"
	"os"
	"strconv"
	"strings"
)

func GetDB() string {
	database := os.Getenv("MYSQL_USER") + ":" + os.Getenv("MYSQL_PASSWORD") + "@tcp(" + os.Getenv("MYSQL_HOST") + ":" + os.Getenv("MYSQL_PORT") + ")/" + os.Getenv("MYSQL_DATABASE")
	return database
}

func GetTimeframes(path string) (int, int, error) {
	from_int, to_int := 0, 4294967295
	u, err := url.Parse(path)
	if err != nil {
		return -1, -1, errors.New("Failed parsing the URL.")
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
	return from_int, to_int, nil
}

func GetPagination(path string) (int, int, error) {
	page_int, per_page_int := 0, 100
	u, err := url.Parse(path)
	if err != nil {
		return -1, -1, errors.New("Failed parsing the URL.")
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
	return page_int, per_page_int, nil
}

func GetDocumentation() []string {
	dat, _ := ioutil.ReadFile("../documentation.md")
	md := markdown.New(markdown.HTML(true))
	return strings.Split(md.RenderToString([]byte(string(dat))), "\n")
}
