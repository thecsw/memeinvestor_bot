package commands

import(
	"errors"

	"../models"
	"./wrap"
)

const(
	NotInFirm = "Not in firm"
	FirmDisbanded = "No memebers left - disbanded firm"
	NewLeader = "CEO left - replaced CEO"
)

func LeaveFirm(params wrap.LeaveFirmWrap) (wrap.LeaveFirmReturnWrap, error){
	investor, err := models.Investors.GetUser(params.Name)
	if err != nil{
		return wrap.LeaveFirmReturnWrap{}, err
	}

	// Check that user is in a firm
	if investor.Firm == 0{
		return wrap.LeaveFirmReturnWrap{}, errors.New(NotInFirm)
	}

	// Remove user from firm
	firm, err := models.Firms.Get(investor.Firm)
	if err != nil{
		return wrap.LeaveFirmReturnWrap{}, err
	}
	firm.Size -= 1
	switch role := investor.FirmRole; role{
	case "trader":
		firm.Traders -= 1
	case "assoc":
		firm.Assocs -= 1
	case "exec":
		firm.Execs -= 1
	case "coo":
		firm.Coo = ""
	case "cfo":
		firm.Cfo = ""
	case "ceo":
		var ceo *models.Investor
		if firm.Cfo != ""{
			firm.Ceo = firm.Cfo
			ceo, _ = models.Investors.GetUser(firm.Ceo)
			ceo.FirmRole = "ceo"
			firm.Cfo = ""
		} else if firm.Coo != ""{
			firm.Ceo = firm.Coo
			ceo, _ = models.Investors.GetUser(firm.Ceo)
			ceo.FirmRole = "ceo"
			firm.Coo = ""
		} else{
			// If nobody has been appointed as new leader, the firm will disband
			models.Firms.Disband(int(firm.Model.ID))
			return wrap.LeaveFirmReturnWrap{FirmName: firm.Name}, errors.New(FirmDisbanded)
		}
		models.Investors.Update(ceo)
		return wrap.LeaveFirmReturnWrap{
			FirmName: firm.Name,
			NewCeoName: ceo.Name,
		}, errors.New(NewLeader)
	}

	err = models.Firms.Update(&firm)
	if err != nil{
		return wrap.LeaveFirmReturnWrap{}, err
	}

	investor.Firm = 0
	investor.FirmRole = ""

	err = models.Investors.Update(&investor)
	if err != nil{
		return wrap.LeaveFirmReturnWrap{}, err
	}

	return wrap.LeaveFirmReturnWrap{}, nil
}