package main

import (
	"fmt"

	"os"
	"os/signal"
	"time"

	"github.com/thecsw/mira"
)

func main() {
	r, _ := mira.Init(mira.ReadCredsFromFile("login.conf"))
	fmt.Println("source | [time] | thing_id | author | submitter | request | time elapsed | status")
	c, stop := r.StreamCommentReplies()
	go func() {
		for {
			go worker(r, <-c)
		}
	}()
	sigint := make(chan os.Signal)
	signal.Notify(sigint, os.Interrupt)
	// Block until received
	<-sigint
	fmt.Printf("Shutting down in %v\n", r.Stream.CommentListInterval*time.Second)
	// Stop the streaming
	stop <- true
	// Just to be sure, sleep for a while
	time.Sleep(r.Stream.CommentListInterval)
	os.Exit(0)
}
