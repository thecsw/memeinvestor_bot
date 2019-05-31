FROM golang

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

RUN go get -u github.com/lib/pq

COPY . .
RUN go build

CMD [ "./appuser" ]