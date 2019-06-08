package models

import (
	"sync"

	"../utils"
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

var (
	db   *gorm.DB
	once sync.Once
)

// Initialize initializes the database
func Initialize() {
	var err error
	once.Do(func() {
		db, err = gorm.Open("postgres", utils.GetDB())
		db.AutoMigrate(
			&Investor{},
			&BrokeHistory{},
			&Badge{},
		)
	})
	if err != nil {
		panic(err)
	}
}

// Close closes the database connection
func Close() {
	db.Close()
}
