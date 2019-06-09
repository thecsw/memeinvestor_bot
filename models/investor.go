package models

import (
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// TableName spits out SQL table name
func (Investor) TableName() string {
	return "investors"
}

// Investor defines investors SQL table 
// Name: string for Reddit username
// Password: string for password field for external clients
// Source: string for source of account ("reddit" or "client")
// Balance: int64 for amount of Memecoins (default 1000)
// Networth: int64 for amount of Memecoins invested (default 1000)
// Firm: int for firm ID of user (default 0)
// FirmRole: string for type of role in firm ("trader", "assoc", "exec", "cfo", "coo", "ceo")
// Banned: bool to check if banned (true, false)
// Admin: bool for admin privileges (true, false)
// Verified: bool for e-mail verification (true, false)
// Email: string for e-mail
// Created: int for UNIX timestamp of creation
// Broke: []BrokeHistory for history of going broke ([InvestorID, Name, Balance])
// Badges: []Badge for badges list (Traders, Assocs, Execs, BoardMems)
type Investor struct {
	gorm.Model

	Name      string `gorm:"not null;unique"`
	Password  string `gorm:"not null;default:''"`
	Source    string `gorm:"not null;default:''"`
	Balance   int64  `gorm:"not null;default:1000"`
	Networth  int64  `gorm:"not null;default:1000"`
	Firm      int    `gorm:"not null;default:0"`
	FirmRole  string `gorm:"not null;default:''"`
	Banned    bool   `gorm:"not null;default:false"`
	Admin     bool   `gorm:"not null;default:false"`
	Verified  bool   `gorm:"not null;default:false"`
	Email     string `gorm:"not null;default:''"`
	Broke     []BrokeHistory
	Badges    []Badge
}
