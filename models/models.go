package models

import (
	"sync"

	"../utils"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

var (
	db   *gorm.DB
	once sync.Once
)

func Initialize() {
	var err error
	once.Do(func() {
		db, err = gorm.Open("postgres", utils.GetDB())
		db.AutoMigrate(
			&Investor{},
			&BrokeHistory{},
		)
	})
	if err != nil {
		panic(err)
	}
}

func Close() {
	db.Close()
}
