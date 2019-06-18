package models

import (
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// TableName spits out SQL table name
func (FirmInvite) TableName() string {
	return "firm_invites"
}

// FirmInvite stores an invite for a user to join a firm
// FirmID: The ID of the firm
// InvestorID: The invited investor
// Accepted: True if the firm invite was accepted
type FirmInvite struct {
	gorm.Model

	FirmID     uint `gorm:"not null"`
	InvestorID uint `gorm:"not null"`
	Accepted   bool `gorm:"default:false"`
}
