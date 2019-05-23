package main

import (
	"fmt"
	"regexp"
	"strings"

	"github.com/thecsw/mira"
)

const (
	HurrayMessage        = `OP u/%NAME% has posted *[THE LINK TO THE TEMPLATE](%LINK%)*, Hurray!`
	TemplateSuccess      = `Template posted successfully!`
	TemplateErrHTTP      = `Your link should start with 'http://' or 'https://'.`
	TemplateErrNotSticky = `You have to reply to the bot's root stickied comment.`
	TemplateErrEdit      = `Failed editing the root sticky: %v`
)

func template(r *mira.Reddit, comment mira.CommentListingDataChildren) error {
	link_r, _ := regexp.Compile(`!template (.+)`)
	link := link_r.FindStringSubmatch(comment.GetBody())[1]
	// Check if its a valid http link
	http_r, _ := regexp.Match(`^https?://.+`, []byte(link))
	if !http_r {
		r.Reply(comment.GetId(), TemplateErrHTTP)
		return nil
	}
	// Check if the parent comment is the bot's sticky
	parent, err := r.GetComment(comment.GetParentId())
	if err != nil {
		return err
	}
	if !parent.IsRoot() {
		r.Reply(comment.GetId(), TemplateErrNotSticky)
		return nil
	}
	// Start editing the comment
	body := parent.GetBody()
	username, _ := regexp.Compile(`u/([-a-zA-Z0-9_]+)`)
	author := username.FindStringSubmatch(body)[1]
	sub, _ := regexp.Compile(`Pss.+`)
	to_edit := HurrayMessage
	to_edit = strings.ReplaceAll(to_edit, "%NAME%", author)
	to_edit = strings.ReplaceAll(to_edit, "%LINK%", link)
	new_body := sub.ReplaceAllString(body, to_edit)
	_, err = r.EditComment(parent.GetId(), new_body)
	if err != nil {
		r.Reply(comment.GetId(), fmt.Sprintf(TemplateErrEdit, err))
		return err
	}
	r.Reply(comment.GetId(), TemplateSuccess)
	return nil
}
