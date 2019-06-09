package commands

import (
	"testing"

	"../models"
	"../utils"
	"./wrap"
)

func TestCreateInvestor(t *testing.T) {
	models.Initialize(utils.GetTestDB())
	type args struct {
		params wrap.CreateInvestorWrap
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
	}{
		{`Create New`, args{wrap.CreateInvestorWrap{Name: `myuser`, Source: `test`}}, false},
		{`Create Same`, args{wrap.CreateInvestorWrap{Name: `myuser`, Source: `testfail`}}, true},
		{`Create Bulk 1`, args{wrap.CreateInvestorWrap{Name: `bulkuser1`, Source: `bulkcreate`}}, false},
		{`Create Bulk 2`, args{wrap.CreateInvestorWrap{Name: `bulkuser2`, Source: `bulkcreate`}}, false},
		{`Create Bulk 3`, args{wrap.CreateInvestorWrap{Name: `bulkuser3`, Source: `bulkcreate`}}, false},
		{`Create Bulk 4`, args{wrap.CreateInvestorWrap{Name: `bulkuser4`, Source: `bulkcreate`}}, false},
		{`Create Bulk 5`, args{wrap.CreateInvestorWrap{Name: `bulkuser5`, Source: `bulkcreate`}}, false},
		{`Create Bulk 6`, args{wrap.CreateInvestorWrap{Name: `bulkuser6`, Source: `bulkcreate`}}, false},
		{`Create Bulk 7`, args{wrap.CreateInvestorWrap{Name: `bulkuser7`, Source: `bulkcreate`}}, false},
		{`Create Bulk 8`, args{wrap.CreateInvestorWrap{Name: `bulkuser8`, Source: `bulkcreate`}}, false},
		{`Create Bulk 9`, args{wrap.CreateInvestorWrap{Name: `bulkuser9`, Source: `bulkcreate`}}, false},
		{`Create Bulk 10`, args{wrap.CreateInvestorWrap{Name: `bulkuser10`, Source: `bulkcreate`}}, false},
		{`Create Bulk 11`, args{wrap.CreateInvestorWrap{Name: `bulkuser11`, Source: `bulkcreate`}}, false},
		{`Create Bulk 12`, args{wrap.CreateInvestorWrap{Name: `bulkuser12`, Source: `bulkcreate`}}, false},
		{`Create Bulk 13`, args{wrap.CreateInvestorWrap{Name: `bulkuser13`, Source: `bulkcreate`}}, false},
		{`Create Bulk 14`, args{wrap.CreateInvestorWrap{Name: `bulkuser14`, Source: `bulkcreate`}}, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := CreateInvestor(tt.args.params); (err != nil) != tt.wantErr {
				t.Errorf("CreateInvestor() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
