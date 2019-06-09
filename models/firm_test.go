package models

import (
	"testing"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func TestFirm_TableName(t *testing.T) {
	type fields struct {
		Model   gorm.Model
		Name    string
		Balance int64
		Size    int
		Ceo     string
		Coo     string
		Cfo     string
		Execs   int
		Assocs  int
		Traders int
		Tax     int
		Level   int
		Private bool
		Payouts []Payout
		Badges  []Badge
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{`Normal`, fields{}, `firms`},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			f := Firm{
				Model:   tt.fields.Model,
				Name:    tt.fields.Name,
				Balance: tt.fields.Balance,
				Size:    tt.fields.Size,
				Ceo:     tt.fields.Ceo,
				Coo:     tt.fields.Coo,
				Cfo:     tt.fields.Cfo,
				Execs:   tt.fields.Execs,
				Assocs:  tt.fields.Assocs,
				Traders: tt.fields.Traders,
				Tax:     tt.fields.Tax,
				Level:   tt.fields.Level,
				Private: tt.fields.Private,
				Payouts: tt.fields.Payouts,
				Badges:  tt.fields.Badges,
			}
			if got := f.TableName(); got != tt.want {
				t.Errorf("Firm.TableName() = %v, want %v", got, tt.want)
			}
		})
	}
}
