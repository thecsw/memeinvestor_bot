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

// Create creates a Firm object
func (p *FirmPlayer) Create(val interface{}) error {
	return p.DB().Create(val).Error
}

// Get gets a Firm object
func (p *FirmPlayer) Get(id int) (*Firm, error) {
	firm := &Firm{}
	err := p.DB().Where("id = ?", id).First(firm).Error
	return firm, err
}

// Get gets a Firm object
func (p *FirmPlayer) GetByName(name string) (*Firm, error) {
	firm := &Firm{}
	err := p.DB().Where("name = ?", name).First(firm).Error
	return firm, err
}

// Exists checks if a certain Firm exists
func (p *FirmPlayer) Exists(name string) bool {
	var count int
	firm := &Firm{}
	p.DB().Where("name = ?", name).Find(firm).Count(&count)
	return count > 0
}

// GetPayouts returns the Firm's history of going broke
func (p *FirmPlayer) GetPayouts(name string) []Payout {
	firm, _ := p.GetByName(name)
	payouts := make([]Payout, 0, 10)
	p.DB().Model(firm).Related(&payouts)
	return payouts
}

// Update updates a value of an Firm object
func (p *FirmPlayer) Update(value interface{}) error {
	return p.DB().Save(value).Error
}

// DB returns the gorm DB model.
func (p *FirmPlayer) DB() *gorm.DB {
	return db
}
