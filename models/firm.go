package models

import (
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// TableName spits out SQL table name
func (Firm) TableName() string {
	return "firms"
}

// Firm defines firms SQL table
// Name: string for firm name
// Balance: int64 for amount of Memecoins (default 1000)
// Size: int for amount of members in firm (default 0)
// Ceo: string for reddit username of CEO (default "")
// Coo: string for reddit username of COO (default "")
// Cfo: string for reddit username of CFO (default "")
// Execs: int for amount of executives in firm (default 0)
// Assocs: int for amount of associates in firm (default 0)
// Traders: int for amount of floor traders in firm (default 0)
// Tax: int for percentage of tax on investors' profits (default 15)
// Level: int for firm upgrade level that CEO has upgraded to (default 1)
// Private: bool for whether firm is private (true, false)
// Created: int for UNIX timestamp of creation
// Payouts: []Payout for history of investor payouts ([InvestorID, Name, Balance])
// Badges: []Badge for badges list ([InvestorID, Name, Title])
type Firm struct {
	gorm.Model

	Name    string `gorm:"not null;unique"`
	Balance int64  `gorm:"not null;default:1000"`
	Size    int    `gorm:"not null;default:0"`
	Ceo     string `gorm:"not null;default:''"`
	Coo     string `gorm:"not null;default:''"`
	Cfo     string `gorm:"not null;default:''"`
	Execs   int    `gorm:"not null;default:0"`
	Assocs  int    `gorm:"not null;default:0"`
	Traders int    `gorm:"not null;default:0"`
	Tax     int    `gorm:"not null;default:15"`
	Level   int    `gorm:"not null;default:1"`
	Private bool   `gorm:"not null;default:false"`
	Created int    `gorm:"not null;unix"`
	Payouts []Payout
	Badges  []Badge
}
