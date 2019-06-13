package commands

import(
	"errors"

	"../models"
	"./wrap"
)

const (
	NotInvited = "Not invited"
	NotFound = "Firm doesn't exist"
)

func JoinFirm(params wrap.JoinFirmWrap) error{
	firm_exists := models.Firms.Exists(params.FirmName)
	if !firm_exists{
		return errors.New(NotFound)
	}

	// Get firm and check for invite
	firm := models.Firms.GetByName(params.FirmName)
	user := models.Investors.GetUser(params.Name)

	// Check for invite if firm is private
	if firm.Private && !invited(firm.Model.ID, user.FirmInvites){
		return errors.New(NotInvited)
	} else{
		user.Firm = firm.Model.ID
		user.FirmRole = "trader"
		firm.Size += 1
		firm.Traders += 1
		user.FirmInvites = remove(firm.Model.ID, user.FirmInvites)
		models.Firms.Update(&firm)
		models.Investors.Update(&user)
	}
}


// Checks whether the firm's ID is in the user's invites list
func invited(firmId int, invites []int) bool{
	for _, id := range invites{
		if firmId == id{
			return true
		}
	}
	return false
}

// Removes the invite once it has been accepted
func remove(firmId int, invites []int) []int{
	index := indexof(firmId, invites)
	invites[index] = invites[len(invites) - 1]
	return invites[:len(invites) - 1]
}

// Indexof function - Go doesn't have one
func indexof(firmId int, invites []int) int{
	for i, e := range invites{
		if firmId == e{
			return i
		}
	}
	return -1
}