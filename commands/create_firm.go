package commands

import(
	"errors"

	"../models"
	"./wrap"
)

const(
	NotEnoughMoney = "Oops! Looks like you don't have enough MemeCoins to create a firm!"
	FirmExists = "Uh oh! That firm already exists!"

	// Investor must have at least 1M memecoin to create a firm
	FirmCreationCost = 1000000
)

func CreateFirm(params wrap.CreateFirmWrap) error{
	firm_exists := models.Firms.Exists(params.Name)
	if firm_exists{
		return errors.New(FirmExists)
	}
	ceo, err := models.Investors.GetUser(params.Creator)
	if err != nil{
		return nil
	}
	if ceo.Balance < FirmCreationCost{
		return errors.New(NotEnoughMoney)
	}

	// Create the new firm
	new_firm := models.Firm{
		Name: params.Name,
		Ceo: params.Creator,
		Size: 1,
	}
	err = models.Firms.Create(&new_firm)
	if err != nil{
		return err
	}

	// Deduct funds from the user's account and place them in the firm
	ceo.Balance -= FirmCreationCost
	ceo.Networth -= FirmCreationCost
	ceo.Firm = int(new_firm.Model.ID)
	ceo.FirmRole = "ceo"
	err = models.Investors.Update(&ceo)
	if err != nil{
		return err
	}

	return nil
}