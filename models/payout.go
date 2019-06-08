package models

import (
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// TableName spits out SQL table name
func (Payout) TableName() string {
	return "payouts"
}

// Payout defines firm payouts for each role
// InvestorID: int of ID of Investor object
// Name: string of username of Investor
// Balance: int64 of balance at time of being broke
type Payout struct {
	gorm.Model

	FirmID     int
	Traders    int64 `gorm:"not null;default"`
	Assocs     int64 `gorm:"not null;unix"`
	Execs      int64 `gorm:"not null;unix"`
	BoardMems  int64 `gorm:"not null;unix"`
	PaidOut    int64 `gorm:"not null;unix"`
}
