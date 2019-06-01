package models

type Image struct {
	Id        int    `mipq:"primary,serial,default=1,"`
	File_type string `mipq:""`
	File_name string `mipq:""`
	File_data []byte `mipq:""`
}
