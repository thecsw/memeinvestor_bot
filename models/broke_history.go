package models

import (
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func (BrokeHistory) TableName() string {
	return "broke_history"
}

type BrokeHistory struct {
	gorm.Model

	InvestorID int
	Name       string
	Balance    int64
}
