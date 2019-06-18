package commands

import (
	"errors"

	"../models"
	"./wrap"
)

const (
	RankTooLow     = "User rank too low"
	AlreadyInvited = "User already invited"
	InFirm         = "User already in firm"
	UserNotFound   = "User not found"
	FirmNotPrivate = "Firm not private"
)

func InviteFirm(params wrap.InviteFirmWrap) (wrap.InviteFirmReturnWrap, error) {
	// Check that target exists
	if !models.Investors.Exists(params.Target) {
		return wrap.InviteFirmReturnWrap{}, errors.New(UserNotFound)
	}

	target, _ := models.Investors.GetUser(params.Target)
	user, _ := models.Investors.GetUser(params.Name)

	// Check user is in a firm
	if user.Firm == 0 {
		return wrap.InviteFirmReturnWrap{}, errors.New(NotInFirm)
	}

	firm, _ := models.Firms.Get(user.Firm)
	invites, _ := models.Invites.GetByFirm(firm.Model.ID)

	// Check that target isn't already in the firm
	if target.Firm == int(firm.Model.ID) {
		return wrap.InviteFirmReturnWrap{}, errors.New(InFirm)
	}

	// Check that firm isn't public
	if !firm.Private {
		return wrap.InviteFirmReturnWrap{}, errors.New(FirmNotPrivate)
	}

	// Check that target isnt already invited
	if invited(invites, target.Model.ID) {
		return wrap.InviteFirmReturnWrap{}, errors.New(AlreadyInvited)
	}

	// Check that user has permission to invite
	if user.FirmRole == "trader" {
		return wrap.InviteFirmReturnWrap{}, errors.New(RankTooLow)
	}

	// Invite user to firm
	newInvite := models.FirmInvite{
		FirmID:     firm.Model.ID,
		InvestorID: target.Model.ID,
	}
	models.Invites.Add(&newInvite)

	return wrap.InviteFirmReturnWrap{
		Name:     target.Name,
		FirmName: firm.Name,
	}, nil
}
