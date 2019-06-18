package wrap

// CreateInvestorWrap does.. something?
type CreateInvestorWrap struct {
	Name   string
	Source string
}

// BalanceInvestorWrap does.. stuff
type BalanceInvestorWrap struct {
	Name   string
	Source string
}

type CreateFirmWrap struct{
	Name    string
	Creator string
}

type LeaveFirmWrap struct{
	Name string
}

type LeaveFirmReturnWrap struct{
	FirmName   string
	NewCeoName string
}

type JoinFirmWrap struct{
	Name     string
	FirmName string
}

type InviteFirmWrap struct{
	Name   string
	Target string
}

type InviteFirmReturnWrap struct{
	Name     string
	FirmName string
}