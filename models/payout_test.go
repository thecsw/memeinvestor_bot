package models

import (
	"testing"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func TestPayout_TableName(t *testing.T) {
	type fields struct {
		Model        gorm.Model
		FirmID       uint
		TraderSize   int64
		TraderAmount int64
		AssocSize    int64
		AssocAmount  int64
		ExecSize     int64
		ExecAmount   int64
		BoardSize    int64
		BoardAmount  int64
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{`Normal`, fields{}, `payouts`},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := Payout{
				Model:        tt.fields.Model,
				FirmID:       tt.fields.FirmID,
				TraderSize:   tt.fields.TraderSize,
				TraderAmount: tt.fields.TraderAmount,
				AssocSize:    tt.fields.AssocSize,
				AssocAmount:  tt.fields.AssocAmount,
				ExecSize:     tt.fields.ExecSize,
				ExecAmount:   tt.fields.ExecAmount,
				BoardSize:    tt.fields.BoardSize,
				BoardAmount:  tt.fields.BoardAmount,
			}
			if got := p.TableName(); got != tt.want {
				t.Errorf("Payout.TableName() = %v, want %v", got, tt.want)
			}
		})
	}
}
