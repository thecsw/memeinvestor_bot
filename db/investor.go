package main

import (
	"database/sql"
	"fmt"
	_ "github.com/lib/pq"
)

const (
	statement = `
CREATE TABLE IF NOT EXISTS Investor (
          ID             SERIAL    NOT NULL PRIMARY KEY,
          NAME           TEXT      NOT NULL,
          CREATED_UTC    REAL      NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW() AT TIME ZONE 'utc'),
          SOURCE         TEXT      NULL     DEFAULT 'none',
          BALANCE        BIGINT    NOT NULL DEFAULT 1000,
          NETWORTH       BIGINT    NOT NULL DEFAULT 1000,
          BROKE          REAL[]    NOT NULL DEFAULT ARRAY[]::REAL[],
          FIRM           INT       NOT NULL DEFAULT 0,
          FIRM_ROLE      TEXT      NOT NULL DEFAULT 'none',
          BADGES         TEXT[]    NOT NULL DEFAULT ARRAY[]::TEXT[],
          LAST_ACTIVE    REAL      NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW() AT TIME ZONE 'utc'),
          LAST_SHARE     REAL      NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW() AT TIME ZONE 'utc'),
          BANNED         BOOL      NOT NULL DEFAULT FALSE,
          ADMIN          BOOL      NOT NULL DEFAULT FALSE,
          MODERATOR      BOOL      NOT NULL DEFAULT FALSE,
          VERIFIED       BOOL      NOT NULL DEFAULT FALSE,
          EMAIL          TEXT      NOT NULL DEFAULT 'none',
          MORE_OPTIONS   TEXT[]    NOT NULL DEFAULT ARRAY[]::TEXT[]
        );
`)

func CreateInvestor() {
	connStr := "user=test password='1234' dbname=db host=postgres port=5432 sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		fmt.Println(err)
		return
	}
	_, err = db.Exec(statement)
	if err != nil {
		fmt.Println(err)
		return
	}
	db.Close()
}
