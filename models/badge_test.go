package models

import (
	"testing"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

func TestBadge_TableName(t *testing.T) {
	type fields struct {
		Model      gorm.Model
		InvestorID uint
		FirmID     uint
		Name       string
		Title      string
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{`Normal`, fields{}, `badges`},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := Badge{
				Model:      tt.fields.Model,
				InvestorID: tt.fields.InvestorID,
				FirmID:     tt.fields.FirmID,
				Name:       tt.fields.Name,
				Title:      tt.fields.Title,
			}
			if got := b.TableName(); got != tt.want {
				t.Errorf("Badge.TableName() = %v, want %v", got, tt.want)
			}
		})
	}
}
