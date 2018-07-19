#!/bin/bash
_now=$(date +"%m_%d_%Y")
_file="/tmp/backup_$_now.sql"
echo "Starting backup to $_file..."
docker-compose exec mysql mysqldump DATABASE_NAME -u USERNAME -p'password' -r "$_file"
echo "Done dumping the database. Copying the file to the host machine..."
docker cp memeinvestor_bot_mysql_1:/tmp/"$_file" ./backups
echo "Done"
