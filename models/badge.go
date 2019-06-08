package models

import (
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// TableName spits out SQL table name
func (Badge) TableName() string {
	return "badges"
}

// Badge defines badges SQL table
// InvestorID: int for ID of investor in Investors
// Name: 
type Badge struct {
	gorm.Model

	InvestorID int
	Name       string
	Title      string
}
