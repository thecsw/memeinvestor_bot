
default: help

help:
	@echo 'help - get this help message'
	@echo 'build - build the containers'
	@echo 'deploy - deploy the containers'
	@echo 'logs - force tail the logs'
	@echo 'stop - stop the containers'
	@echo 'down - stop and wipe out the network'

build:
	docker-compose build

deploy:
	docker-compose up -d

logs:
	docker-compose logs -f --tail 100

stop:
	docker-compose stop

down:
	docker-compose down
