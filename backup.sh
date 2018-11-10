#!/bin/bash
echo "Trying to create a backups folder..."
mkdir backups
_now=$(date +"%m_%d_%Y")
_file="/tmp/backup_$_now.sql"
echo "Starting backup to $_file..."
docker exec memeinvestor_bot_mysql_1 mysqldump mysql -u mysql -p'strongpass!word' -r "$_file"
echo "Done dumping the database. Copying the file to the host machine..."
docker cp memeinvestor_bot_mysql_1:$_file $1
echo "Done"
