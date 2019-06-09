package commands

import (
	"testing"

	"../models"
	"../utils"
	"./wrap"
)

func TestBalanceInvestor(t *testing.T) {
	models.Initialize(utils.GetTestDB())
	type args struct {
		params wrap.BalanceInvestorWrap
	}
	tests := []struct {
		name    string
		args    args
		want    int64
		wantErr bool
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := BalanceInvestor(tt.args.params)
			if (err != nil) != tt.wantErr {
				t.Errorf("BalanceInvestor() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("BalanceInvestor() = %v, want %v", got, tt.want)
			}
		})
	}
}
