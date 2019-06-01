// MIB Investor Table Initialization
//
// This file introduces a method called InitInvestor() that creates
// a new table Investor if one doesn't exist already. Please note that
// all of the fields have a default value except the name. Ideally,
// the SQL query to add a new user would be just as simple as
//  db # INSERT INTO Investor (name) VALUES ('username');
//
// Please find the full table description below:
//  - ID: The unique numeric id of the user. Auto-incrementing.
//  - NAME: The name of the user. Cannot be defaulted and should be unique.
//  - CREATED_UTC: UNIX timestamp of user's account creation.
//  - SOURCE: Where the account was created.
// MIB is working on r/MemeEconomy subreddit right now, but in the future
// we have plans on expanding to the web. SOURCE can have values like
// 'r/MemeEconomy' or 'web' to show where the account was created.
//  - BALANCE: Current balance of the user. Consider this as cash. Available balance.
//  - NETWORTH: Balance of the user with all assets included. This is just assets.
//  - BROKE: If a user gone broke, this is an array of UNIX timestamps when user was broke.
//  - FIRM: If the user is in a firm, it will have a value other than 0.
//  - PREV_FIRMS: An array of previous firms' IDs.
//  - FIRM_ROLE: If the user is in a firm he will have a position there. Like 'ceo'.
//  - BADGES: Array of badges' names. Something like ['donor', 'contributor']
//  - LAST_ACTIVE: UNIX timestamp of last command issued by the user.
//  - LAST_SHARE: UNIX timestamp of last bought share/stock.
//  - BANNED: If the user is banned. If true, do not serve them.
//  - ADMIN: If the user is admin. Full admin privileges from CLI.
//  - VERIFIED: If the user is verified. If they register on the website,
// this just confirms that their web account is linked to their reddit account.
//  - EMAIL: Email address of the user.
//  - MORE_OPTIONS: Array of some different future or small options.
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
          NAME           TEXT      NOT NULL UNIQUE,
          CREATED_UTC    INT       NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW() AT TIME ZONE 'utc'),
          SOURCE         TEXT      NOT NULL DEFAULT 'none',
          BALANCE        BIGINT    NOT NULL DEFAULT 1000,
          NETWORTH       BIGINT    NOT NULL DEFAULT 1000,
          BROKE          INT[]     NOT NULL DEFAULT ARRAY[]::INT[],
          FIRM           INT       NOT NULL DEFAULT 0,
          PREV_FIRMS     INT[]     NOT NULL DEFAULT ARRAY[]::INT[],
          FIRM_ROLE      TEXT      NOT NULL DEFAULT 'none',
          BADGES         TEXT[]    NOT NULL DEFAULT ARRAY[]::TEXT[],
          LAST_ACTIVE    INT       NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW() AT TIME ZONE 'utc'),
          LAST_SHARE     INT       NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW() AT TIME ZONE 'utc'),
          BANNED         BOOL      NOT NULL DEFAULT FALSE,
          ADMIN          BOOL      NOT NULL DEFAULT FALSE,
          VERIFIED       BOOL      NOT NULL DEFAULT FALSE,
          EMAIL          TEXT      NOT NULL DEFAULT 'none',
          MORE_OPTIONS   TEXT[]    NOT NULL DEFAULT ARRAY[]::TEXT[]
        );
`)

func InitInvestor() {
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
