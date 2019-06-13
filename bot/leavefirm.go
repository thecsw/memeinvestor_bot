package main

import(
	"fmt"

	"../commands"
	"../commands/wrap"
	"github.com/thecsw/mira"
)

const(
	NotInFirm = "You aren't currently in a firm."
	FirmDisbanded = "You have left %s and it has been disbanded."
	NewLeader = "You have left %s as CEO, %s will take your place."
	LeftFirm = "You have successfully left your firm."
)

func leavefirm(r *mira.Reddit, comment mira.Comment) error{
	returned, err := commands.LeaveFirm(wrap.LeaveFirmWrap{
		Name: comment.GetAuthor(),
	})

	if err != nil{
		if err.Error() == commands.NotInFirm{
			r.Reply(comment.GetId(), NotInFirm)
		} else if err.Error() == commands.FirmDisbanded{
			r.Reply(comment.GetId(), fmt.Sprintf(FirmDisbanded, returned.FirmName))
		} else if err.Error() == commands.NewLeader{
			r.Reply(comment.GetId(), fmt.Sprintf(NewLeader, returned.FirmName, returned.NewCeoName))
		}
		return err
	}

	r.Reply(comment.GetId(), LeftFirm)

	return nil
}