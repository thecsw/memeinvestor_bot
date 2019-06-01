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