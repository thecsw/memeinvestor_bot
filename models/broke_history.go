package models

import (
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// TableName spits out SQL table name
func (BrokeHistory) TableName() string {
	return "broke_history"
}

// BrokeHistory defines array of history gone broke
// InvestorID: int of ID of Investor object
// Name: string of username of Investor
// Balance: int64 of balance at time of being broke
type BrokeHistory struct {
	gorm.Model

	InvestorID uint
	Name       string
	Balance    int64
}
