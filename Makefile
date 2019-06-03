
cc =

default: help

help:
	@echo 'help                             - get this help message'
	@echo 'build   [OPTIONAL: cc=services]  - build the containers'
	@echo 'deploy  [OPTIONAL: cc=services]  - deploy the containers'
	@echo 'logs    [OPTIONAL: cc=services]  - force tail the logs'
	@echo 'stop    [OPTIONAL: cc=services]  - stop the containers'
	@echo 'down                             - stop and wipe out the network'
	@echo 'status                           - get statuses on all containers'
	@echo 'format                           - format all go files in this directory'

build:
	docker-compose build $(cc)

deploy:
	docker-compose up -d postgres
	@echo 'Sleeping for 20 seconds...'
	sleep 20
	docker-compose up -d $(cc)

logs:
	docker-compose logs -f --tail 100 $(cc)

stop:
	docker-compose stop $(cc)

down:
	docker-compose down

status:
	docker-compose ps

format:
	find . -type f | grep '\.go$' | xargs gofmt -w && find . -type f | grep '\.go$' | xargs goimports -w
