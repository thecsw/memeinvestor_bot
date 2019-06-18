package commands

import (
	"errors"

	"../models"
	"./wrap"
)

const (
	NotInvited    = "Not invited"
	NotFound      = "Firm doesn't exist"
	AlreadyInFirm = "User is in another firm"
)

func JoinFirm(params wrap.JoinFirmWrap) error {
	firm_exists := models.Firms.Exists(params.FirmName)
	if !firm_exists {
		return errors.New(NotFound)
	}

	// Get firm and check for invite
	firm, _ := models.Firms.GetByName(params.FirmName)
	user, _ := models.Investors.GetUser(params.Name)

	invites, _ := models.Invites.GetByFirm(firm.Model.ID)

	// Check that user isn't already in a firm
	if user.Firm != 0 {
		return errors.New(AlreadyInFirm)
	}

	// Check for invite if firm is private
	if firm.Private && !invited(invites, user.Model.ID) {
		return errors.New(NotInvited)
	} else {
		user.Firm = int(firm.Model.ID)
		user.FirmRole = "trader"
		firm.Size++
		firm.Traders++
		if invited(invites, user.Model.ID) {
			invites[indexof(invites, user.Model.ID)].Accepted = true
		}
		models.Firms.Update(&firm)
		models.Investors.Update(&user)
		err := models.Invites.Update(invites)
		if err != nil {
			return err
		}
	}

	return nil
}

// Checks whether the firm's ID is in the user's invites list
func invited(firmInvites []models.FirmInvite, investorID uint) bool {
	for _, invite := range firmInvites {
		if invite.InvestorID == investorID && !invite.Accepted {
			return true
		}
	}
	return false
}

// Removes the invite once it has been accepted
func remove(firmInvites []models.FirmInvite, investorID uint) []models.FirmInvite {
	index := indexof(firmInvites, investorID)
	firmInvites[index] = firmInvites[len(firmInvites)-1]
	return firmInvites[:len(firmInvites)-1]
}

// Indexof function - Go doesn't have one
func indexof(firmInvites []models.FirmInvite, investorID uint) int {
	for i, e := range firmInvites {
		if e.InvestorID == investorID {
			return i
		}
	}
	return -1
}
