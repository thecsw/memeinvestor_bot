package main

import(
	"fmt"

	"../commands"
	"github.com/thecsw/mira"
)

const(
	// For some reason Reddit requires two newline chars to display one
	TopBody = "Investors with the highest Net Worth:\n\n"
	TopLine = `\#` + "%d  -  %s  :  %d M\u00A2\n\n"
)

func top(r *mira.Reddit, comment mira.Comment) error{
	top, err := commands.GetTop()
	if err != nil{
		return err
	}

	body := TopBody
	for i, investor := range top{
		body += fmt.Sprintf(TopLine, i + 1, investor.Name, investor.Networth)
	}

	r.Reply(comment.GetId(), body)

	return nil
}