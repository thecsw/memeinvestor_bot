package main

import(
	"fmt"
	"regexp"

	"../commands"
	"../commands/wrap"
	"github.com/thecsw/mira"
)

const(
	RankTooLow = "You do not have permission to invite people to your firm."
	AlreadyInvited = "That user is already invited to your firm."
	InFirm = "That user is already in your firm."
	NotInAFirm = "You are not in a firm."
	UserNotFound = "That user doesn't exist."
	Invited = "Successfully invited %s to join %s."
)

func invitefirm(r *mira.Reddit, comment mira.Comment) error{
	user_r, _ := regexp.Compile(`!invitefirm (.+)`)
	user := user_r.FindStringSubmatch(comment.GetBody())[1]

	returned, err := commands.InviteFirm(wrap.InviteFirmWrap{
		Name: comment.GetAuthor(),
		Target: user,
	})

	if err != nil{
		if err.Error() == commands.RankTooLow{
			r.Reply(comment.GetId(), RankTooLow)
		} else if err.Error() == commands.AlreadyInvited{
			r.Reply(comment.GetId(), AlreadyInvited)
		} else if err.Error() == commands.InFirm{
			r.Reply(comment.GetId(), InFirm)
		} else if err.Error() == commands.UserNotFound{
			r.Reply(comment.GetId(), UserNotFound)
		} else if err.Error() == commands.NotInFirm{
			r.Reply(comment.GetId(), NotInAFirm)
		}
		return err
	}

	r.Reply(comment.GetId(), fmt.Sprintf(Invited, returned.Name, returned.FirmName))

	return nil
}