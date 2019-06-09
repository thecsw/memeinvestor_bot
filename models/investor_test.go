package models

import (
	"testing"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func TestInvestor_TableName(t *testing.T) {
	type fields struct {
		Model    gorm.Model
		Name     string
		Password string
		Source   string
		Balance  int64
		Networth int64
		Firm     int
		FirmRole string
		Banned   bool
		Admin    bool
		Verified bool
		Email    string
		Broke    []BrokeHistory
		Badges   []Badge
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{`Normal`, fields{}, `investors`},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			i := Investor{
				Model:    tt.fields.Model,
				Name:     tt.fields.Name,
				Password: tt.fields.Password,
				Source:   tt.fields.Source,
				Balance:  tt.fields.Balance,
				Networth: tt.fields.Networth,
				Firm:     tt.fields.Firm,
				FirmRole: tt.fields.FirmRole,
				Banned:   tt.fields.Banned,
				Admin:    tt.fields.Admin,
				Verified: tt.fields.Verified,
				Email:    tt.fields.Email,
				Broke:    tt.fields.Broke,
				Badges:   tt.fields.Badges,
			}
			if got := i.TableName(); got != tt.want {
				t.Errorf("Investor.TableName() = %v, want %v", got, tt.want)
			}
		})
	}
}
