package models

import (
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

type InvestorPlayer struct {
	db *gorm.DB
}

var (
	Investors = &InvestorPlayer{db: nil}
)

func (p *InvestorPlayer) Create(val interface{}) error {
	return p.DB().Create(val).Error
}

func (p *InvestorPlayer) GetUser(name string) (*Investor, error) {
	investor := &Investor{}
	err := p.DB().Where("name = ?", name).First(investor).Error
	return investor, err
}

func (p *InvestorPlayer) Exists(name string) bool {
	var count int
	var investor Investor
	p.DB().Where("name = ?", name).Find(&investor).Count(&count)
	return count > 0
}

func (p *InvestorPlayer) GetBrokeHistory(name string) []BrokeHistory {
	investor := &Investor{}
	brokes := make([]BrokeHistory, 0, 10)
	p.DB().Model(investor).Related(&brokes)
	return brokes
}

func (p *InvestorPlayer) GoneBroke(name string) error {
	investor, _ := p.GetUser(name)
	return p.DB().Create(&BrokeHistory{
		Name:    investor.Name,
		Balance: investor.Balance,
	}).Error
}

func (p *InvestorPlayer) Update(value interface{}) error {
	investor := &Investor{}
	return p.DB().Model(investor).Save(value).Error
}

func (p *InvestorPlayer) DB() *gorm.DB {
	return db
}
