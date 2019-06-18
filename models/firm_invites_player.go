package models

import (
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// FirmInvitePlayer declares DB model for Invite table
type FirmInvitePlayer struct {
	db *gorm.DB
}

var (
	// Invites declares Invite table
	Invites = &FirmInvitePlayer{db: nil}
)

// GetByFirm takes the ID of a firm and returns an array of all their associated invites
func (p *FirmInvitePlayer) GetByFirm(firm uint) ([]FirmInvite, error) {
	var invites []FirmInvite
	err := p.DB().Where("firm_id = ?", firm).Find(&invites).Error
	return invites, err
}

// Add adds an invite to the table
func (p *FirmInvitePlayer) Add(val interface{}) error {
	return p.DB().Create(val).Error
}

// Update takes a list of FirmInvites and updates all of them in the db
func (p *FirmInvitePlayer) Update(inviteList []FirmInvite) error {
	for _, v := range inviteList {
		err := p.DB().Save(&v).Error
		if err != nil {
			return err
		}
	}
	return nil
}

// Returns the database
func (p *FirmInvitePlayer) DB() *gorm.DB {
	return db
}
