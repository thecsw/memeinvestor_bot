package utils

import (
	"os"
	"strconv"
	"net/url"
	"errors"
)

func GetDB() string {
	database := os.Getenv("MYSQL_USER") + ":" + os.Getenv("MYSQL_PASSWORD") + "@tcp(" + os.Getenv("MYSQL_HOST") + ":" + os.Getenv("MYSQL_PORT") + ")/" + os.Getenv("MYSQL_DATABASE")
	return database
}

func GetTimeframes(path string) (string, string, error) {
	from_int, to_int := 0, 0
	u, err := url.Parse(path)
	if err != nil {
		return "", "", errors.New("Failed parsing the URL.")
	}
	queries := u.Query()
	if val, ok := queries["from"]; ok {
		from_int, err = strconv.Atoi(val[0])
		if err != nil {
			return "", "", errors.New("Failed converting 'from' argument.")			
		}
	}
	if val, ok := queries["to"]; ok {
		to_int, err = strconv.Atoi(val[0])
		if err != nil {
			return "", "", errors.New("Failed converting 'to' argument.")			
		}
	}
	err = nil
	if from_int == 0 || to_int == 0 {
		return "", "", errors.New("Some arguments were not provided.")
	}
	return strconv.Itoa(from_int), strconv.Itoa(to_int), nil
}
