package models

import (
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func (Investor) TableName() string {
	return "investors"
}

type Investor struct {
	gorm.Model

	Name      string `gorm:"not null;unique"`
	Password  string `gorm:"not null;default:''"`
	Source    string `gorm:"not null;default:''"`
	Balance   int64  `gorm:"not null;default:1000"`
	Networth  int64  `gorm:"not null;default:1000"`
	Firm      int    `gorm:"not null;default:0"`
	Firm_role string `gorm:"not null;default:''"`
	Banned    bool   `gorm:"not null;default:false"`
	Admin     bool   `gorm:"not null;default:false"`
	Verified  bool   `gorm:"not null;default:false"`
	Email     string `gorm:"not null;default:''"`
	Broke     []BrokeHistory
	Badges    []Badge
}
