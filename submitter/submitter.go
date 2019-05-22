package main

import (
	"fmt"
	"github.com/thecsw/mira"
	"os"
	"os/signal"
	"time"
	"strings"
)

func main() {
	// Authenticate
	r, _ := mira.Init(mira.ReadCredsFromFile("login.conf"))
	// Get handler to listen
	c, stop := r.StreamNewPosts("memeinvestor_test")
	fmt.Println("source | [time] | thing_id | author | submitter | time elapsed")
	go func() {
		for {
			post := <-c
			start := time.Now()
			to_post := StickyComment
			to_post += strings.ReplaceAll(AttachSource, "%NAME%", post.GetAuthor())
			comment, _ := r.Comment(post.GetId(), to_post)
			r.Distinguish(comment.GetId(), "yes", true)
			finish := time.Now()
			// Output the worker log
			fmt.Printf("%v [%v] %v %v %v %v\n",
				"submitter",
				start.Format(time.RFC1123),
				post.GetId(),
				post.GetAuthor(),
				post.GetSubreddit(),
				finish.Sub(start),
			)
		}
	}()
	sigint := make(chan os.Signal)
	signal.Notify(sigint, os.Interrupt)
	// Block until received
	<-sigint
	fmt.Printf("Shutting down in %v\n", r.Stream.PostListInterval * time.Second)
	// Stop the streaming
	stop <- true
	// Just to be sure, sleep for a while
	time.Sleep(r.Stream.PostListInterval)
	os.Exit(0)
}
