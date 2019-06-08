package models

import (
	"github.com/jinzhu/gorm"

	// Register Postgres dialect
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

// InvestorPlayer declares DB model for Investors table
type InvestorPlayer struct {
	db *gorm.DB
}

var (
	// Investors declares Investors table
	Investors = &InvestorPlayer{db: nil}
)

// Create creates an Investor object
func (p *InvestorPlayer) Create(val interface{}) error {
	return p.DB().Create(val).Error
}

// GetUser gets an Investor object
func (p *InvestorPlayer) GetUser(name string) (*Investor, error) {
	investor := &Investor{}
	err := p.DB().Where("name = ?", name).First(investor).Error
	return investor, err
}

// Exists checks if a certain Investor exists
func (p *InvestorPlayer) Exists(name string) bool {
	var count int
	var investor Investor
	p.DB().Where("name = ?", name).Find(&investor).Count(&count)
	return count > 0
}

// GetBrokeHistory returns the Investor's history of going broke
func (p *InvestorPlayer) GetBrokeHistory(name string) []BrokeHistory {
	investor := &Investor{}
	brokes := make([]BrokeHistory, 0, 10)
	p.DB().Model(investor).Related(&brokes)
	return brokes
}

// GoneBroke resets the Investor's balance to 1000
func (p *InvestorPlayer) GoneBroke(name string) error {
	investor, _ := p.GetUser(name)
	return p.DB().Create(&BrokeHistory{
		Name:    investor.Name,
		Balance: investor.Balance,
	}).Error
}

// Update updates a value of an Investor object
func (p *InvestorPlayer) Update(value interface{}) error {
	investor := &Investor{}
	return p.DB().Model(investor).Save(value).Error
}

// DB returns the gorm DB model.
func (p *InvestorPlayer) DB() *gorm.DB {
	return db
}
