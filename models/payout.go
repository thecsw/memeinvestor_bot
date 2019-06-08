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

	FirmID       int
	TraderSize   int64 `gorm:"not null;default:0"`
	TraderAmount int64 `gorm:"not null;default:0"`
	AssocSize    int64 `gorm:"not null;default:0"`
	AssocAmount  int64 `gorm:"not null;default:0"`
	ExecSize     int64 `gorm:"not null;default:0"`
	ExecAmount   int64 `gorm:"not null;default:0"`
	BoardSize    int64 `gorm:"not null;default:0"`
	BoardAmount  int64 `gorm:"not null;default:0"`
}
