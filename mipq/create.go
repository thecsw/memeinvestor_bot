package mipq

import (
	"fmt"
	"reflect"
	"regexp"
	"strings"
)

func getsl(p reflect.Type) string {
	return fmt.Sprintf("%s", p)
}

func CreateTable(param interface{}) string {
	t := reflect.TypeOf(param)
	tagname := "mipq"
	defreg, _ := regexp.Compile(`default=(.+),`)
	create := "CREATE TABLE IF NOT EXISTS "
	create += t.Name() + " ("
	for i := 0; i < t.NumField(); i++ {
		// Define the DB type and default value
		defval := ""
		newtype := ""
		unique := ""
		primary := ""
		null := "NULL"
		field := t.Field(i)
		// Get all fields!
		name := field.Name
		fulltype := getsl(field.Type)
		justtype := strings.ReplaceAll(fulltype, "[]", "")
		options := field.Tag.Get(tagname)
		// Make the new type for the DB
		switch justtype {
		case "int32":
			newtype = "INT"
		case "int64":
			newtype = "BIGINT"
		case "int":
			newtype = "INT"
		case "string":
			newtype = "TEXT"
		case "bool":
			newtype = "BOOL"
		case "byte":
			newtype = "BYTEA"
		}
		// Check if it is serial
		if tmp, _ := regexp.Match(`serial`, []byte(options)); tmp {
			newtype = "SERIAL"
		}
		// Check if it should be unique
		if tmp, _ := regexp.Match(`unique`, []byte(options)); tmp {
			unique = "UNIQUE"
		}
		// Check if it's a primary key
		if tmp, _ := regexp.Match(`primary`, []byte(options)); tmp {
			primary = "PRIMARY KEY"
		}
		// By default, it's always not null. Say null to make it null
		if tmp, _ := regexp.Match(`null`, []byte(options)); !tmp {
			null = "NOT " + null
		}
		// Make it a UNIX Now timestamp as default value
		if tmp, _ := regexp.Match(`unix`, []byte(options)); tmp {
			defval = "EXTRACT(EPOCH FROM NOW() AT TIME ZONE 'utc')"
		}
		// Check if default value is found
		if tmp, _ := regexp.Match(`default=(.+),`, []byte(options)); tmp {
			defval = defreg.FindStringSubmatch(options)[1]
		}
		// Set empty array default if it's an array
		if tmp, _ := regexp.Match(`\[]`, []byte(fulltype)); tmp {
			defval = "ARRAY[]::" + newtype + "[]"
			newtype += "[]"
		}
		// If default value exists, prepend DEFAULT string
		if defval != "" {
			defval = "DEFAULT " + defval
		}
		create += fmt.Sprintf("\n\t %s %s %s %s %s %s",
			name,
			newtype,
			null,
			primary,
			unique,
			defval,
		)
		// Construct a string
		//create += "\n\t" + name + " " + newtype + null + primary+ unique + defval
		if i < t.NumField()-1 {
			create += ","
		}
	}
	create += "\n);"
	return create
}
