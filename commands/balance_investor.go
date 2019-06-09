package commands

import (
	"../models"
	"./wrap"
)

func BalanceInvestor(params wrap.BalanceInvestorWrap) (int64, error) {
	investor, err := models.Investors.GetUser(params.Name)
	if err != nil {
		return 0, err
	}
	return investor.Balance, nil
}
