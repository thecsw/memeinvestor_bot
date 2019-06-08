package models

import (
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func (Badge) TableName() string {
	return "badges"
}

type Badge struct {
	gorm.Model

	InvestorID int
	Name string
	Title string
}
