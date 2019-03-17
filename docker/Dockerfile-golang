FROM golang

RUN go get -u github.com/go-sql-driver/mysql
RUN go get -u github.com/gorilla/mux

WORKDIR /app

COPY api/ .

RUN go build api.go