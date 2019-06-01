package models

type Investor struct {
	Id           int      `mipq:"primary,serial"`
	Name         string   `mipq:"unique"`
	Created_utc  int      `mipq:"unix"`
	Source       string   `mipq:"default='none',"`
	Balance      int64    `mipq:"default=1000,"`
	Networth     int64    `mipq:"default=1000,"`
	Broke        []int    `mipq:""`
	Firm         int      `mipq:"default=0,"`
	Prev_firms   []int    `mipq:""`
	Firm_role    string   `mipq:"default='none',"`
	Badges       []string `mipq:""`
	Last_active  int      `mipq:"unix"`
	Last_share   int      `mipq:"unix"`
	Banned       bool     `mipq:"default=false,"`
	Admin        bool     `mipq:"default=false,"`
	Verified     bool     `mipq:"default=false,"`
	Email        string   `mipq:"default='none',"`
	Avatar       int      `mipq:"default=0,"`
	More_options []string `mipq:""`
}
