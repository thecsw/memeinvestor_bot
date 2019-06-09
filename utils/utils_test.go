package utils

import "testing"

func TestGetTestDB(t *testing.T) {
	tests := []struct {
		name string
		want string
	}{
		{"GetTestDB", "user=test password=pass dbname=db host=localhost port=9123 sslmode=disable"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := GetTestDB(); got != tt.want {
				t.Errorf("GetTestDB() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestRegMatch(t *testing.T) {
	type args struct {
		pattern string
		text    string
	}
	tests := []struct {
		name string
		args args
		want bool
	}{
		{`Normal !create`, args{pattern: `!create`, text: `!create`}, true},
		{`Bad !create`, args{pattern: `!create`, text: `!crate`}, false},
		{`Normal !balance`, args{pattern: `!balance`, text: `!balance`}, true},
		{`Bad !balance`, args{pattern: `!balance`, text: `!blance`}, false},
		{`Normal !invest (.+)`, args{pattern: `!invest (.+)`, text: `!invest 100`}, true},
		{`Bad !invest (.+)`, args{pattern: `!invest (.+)`, text: `!invest100`}, false},
		{`Normal !invest (\d+)`, args{pattern: `!invest (\d+)`, text: `!invest 100`}, true},
		{`Bad !invest (\d+)`, args{pattern: `!invest (\d+)`, text: `!invest bad`}, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := RegMatch(tt.args.pattern, tt.args.text); got != tt.want {
				t.Errorf("RegMatch() = %v, want %v", got, tt.want)
			}
		})
	}
}
