
cc = ""

default: help

help:
	@echo 'help                             - get this help message'
	@echo 'build   [OPTIONAL: cc=services]  - build the containers'
	@echo 'deploy  [OPTIONAL: cc=services]  - deploy the containers'
	@echo 'logs    [OPTIONAL: cc=services]  - force tail the logs'
	@echo 'stop    [OPTIONAL: cc=services]  - stop the containers'
	@echo 'down                             - stop and wipe out the network'
	@echo 'test				- run tests'

build:
	docker-compose build $(cc)

deploy:
	docker-compose up -d $(cc)

logs:
	docker-compose logs -f --tail 100 $(cc)

stop:
	docker-compose stop $(cc)

down:
	docker-compose down

test:
	@echo -n 'Starting the database...'
	@docker-compose up -d testPostgres 2>&1 >/dev/null
	@echo ' DONE'
	@echo -n 'Waiting for database bootup...'
	@sleep 10
	@echo ' DONE'
	go test -v ./...
	@echo -n 'Killing the database...'
	@docker-compose stop testPostgres 2>&1 >/dev/null
	@docker rm memeinvestor_bot_testPostgres_1
	@echo ' DONE'
