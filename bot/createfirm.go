package main

import (
	"fmt"
	"regexp"

	"../commands"
	"../commands/wrap"
	"github.com/thecsw/mira"
)

const(
	Success = "Successfully created your new firm! You are now CEO of %s."
)

func createfirm(r *mira.Reddit, comment mira.Comment) error{
	firm_name_r, _ := regexp.Compile(`!createfirm (.+)`)
	firm_name := firm_name_r.FindStringSubmatch(comment.GetBody())[1]

	err := commands.CreateFirm(wrap.CreateFirmWrap{
		Name: firm_name,
		Creator: comment.GetAuthor(),
	})

	if err != nil{
		if err.Error() == commands.FirmExists{
			r.Reply(comment.GetId(), err.Error())
		}
		if err.Error() == commands.NotEnoughMoney{
			r.Reply(comment.GetId(), err.Error())
		}
		return err
	}

	body := fmt.Sprintf(Success, firm_name)

	r.Reply(comment.GetId(), body)

	return nil
}