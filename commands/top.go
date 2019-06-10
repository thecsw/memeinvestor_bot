package commands

import(
	"../utils"
	"../models"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func GetTop() ([]models.Investor, error){
	db, err := gorm.Open("postgres", utils.GetDB())
	top := []models.Investor{}
	db.Order("networth desc").Limit(5).Find(&top)

	return top, err
}