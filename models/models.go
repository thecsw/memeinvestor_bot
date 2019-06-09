package models

import (
	"sync"

	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

var (
	db   *gorm.DB
	once sync.Once
)

// Initialize initializes the database
func Initialize(dbCreds string) {
	var err error
	once.Do(func() {
		db, err = gorm.Open("postgres", dbCreds)
		AutoMigrate(db)
	})
	if err != nil {
		panic(err)
	}
}

// Close closes the database connection
func Close() {
	db.Close()
}

func AutoMigrate(temp *gorm.DB) {
	temp.AutoMigrate(
		&Investor{},
		&BrokeHistory{},
		&Badge{},
		&Payout{},
		&Firm{},
	)
}
