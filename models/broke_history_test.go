package models

import (
	"testing"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func TestBrokeHistory_TableName(t *testing.T) {
	type fields struct {
		Model      gorm.Model
		InvestorID uint
		Name       string
		Balance    int64
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{`Normal`, fields{}, "broke_history"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := BrokeHistory{
				Model:      tt.fields.Model,
				InvestorID: tt.fields.InvestorID,
				Name:       tt.fields.Name,
				Balance:    tt.fields.Balance,
			}
			if got := b.TableName(); got != tt.want {
				t.Errorf("BrokeHistory.TableName() = %v, want %v", got, tt.want)
			}
		})
	}
}
