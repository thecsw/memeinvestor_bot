package commands

import (
	"errors"

	"../models"
	"./wrap"
)

func CreateInvestor(params wrap.CreateInvestorWrap) error {
	if models.Investors.Exists(params.Name) {
		return errors.New("Account already exists.")
	}
	return models.Investors.Create(&models.Investor{
		Name:   params.Name,
		Source: params.Source,
	})
}
