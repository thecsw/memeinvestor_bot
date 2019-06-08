package models

import (
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// FirmPlayer declares DB model for Firms table
type FirmPlayer struct {
	db *gorm.DB
}

var (
	// Firms declares Firms table
	Firms = &FirmPlayer{db: nil}
)

// Create creates an Firm object
func (p *FirmPlayer) Create(val interface{}) error {
	return p.DB().Create(val).Error
}

// Get gets an Firm object
func (p *FirmPlayer) Get(id int) (*Firm, error) {
	Firm := &Firm{}
	err := p.DB().Where("id = ?", id).First(Firm).Error
	return Firm, err
}

// Exists checks if a certain Firm exists
func (p *FirmPlayer) Exists(id int) bool {
	var count int
	var Firm Firm
	p.DB().Where("id = ?", id).Find(&Firm).Count(&count)
	return count > 0
}

// GetPayouts returns the Firm's history of going broke
func (p *FirmPlayer) GetPayouts(name string) []Payout {
	Firm := &Firm{}
	payouts := make([]Payout, 0, 10)
	p.DB().Model(Firm).Related(&payouts)
	return payouts
}

// Update updates a value of an Firm object
func (p *FirmPlayer) Update(value interface{}) error {
	Firm := &Firm{}
	return p.DB().Model(Firm).Save(value).Error
}

// DB returns the gorm DB model.
func (p *FirmPlayer) DB() *gorm.DB {
	return db
}
