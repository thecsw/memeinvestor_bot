FROM golang

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

RUN go get -u github.com/lib/pq
RUN go get github.com/thecsw/mira

COPY . .
RUN go build -o bot_exec ./bot

CMD [ "./bot_exec" ]