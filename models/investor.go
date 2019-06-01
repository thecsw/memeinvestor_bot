package models

type Investor struct {
	Id           int      `migdo:"primary,serial"`
	Name         string   `migdo:"unique"`
	Created_utc  int      `migdo:"unix"`
	Source       string   `migdo:"default='none',"`
	Balance      int64    `migdo:"default=1000,"`
	Networth     int64    `migdo:"default=1000,"`
	Broke        []int    `migdo:""`
	Firm         int      `migdo:"default=0,"`
	Prev_firms   []int    `migdo:""`
	Firm_role    string   `migdo:"default='none',"`
	Badges       []string `migdo:""`
	Last_active  int      `migdo:"unix"`
	Last_share   int      `migdo:"unix"`
	Banned       bool     `migdo:"default=false"`
	Admin        bool     `migdo:"default=false"`
	Verified     bool     `migdo:"default=false"`
	Email        string   `migdo:"default='none',"`
	More_options []string `migdo:""`
}
