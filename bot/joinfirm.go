package main

import(
	"fmt"
	"regexp"

	"../commands"
	"../commands/wrap"
	"github.com/thecsw/mira"
)

const(
	NotInvited = "You have not been invited to that firm."
	NotFound = "That firm doesn't exist."
	Joined = "You have successfully joined %s as a Floor Trader."
)

func joinfirm(r *mira.Reddit, comment mira.Comment) error{
	firm_name_r := regexp.Compile(`!joinfirm (.+)`)
	firm_name := firm_name_r.FindStringSubmatch(comment.GetBody())[1]

	err := commands.JoinFirm(wrap.JoinFirmWrap{
		Name: comment.GetAuthor(),
		Firm: firm_name,
	})

	if err != nil{
		if err.Error() == commands.NotInvited{
			r.Reply(comment.GetId(), NotInvited)
		} else if err.Error() == commands.NotFound{
			r.Reply(comment.GetId(), NotFound)
		}
		return err
	}

	r.Reply(comment.GetId(), fmt.Sprintf(Joined, firm_name))

	return nil
}