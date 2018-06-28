#!/bin/bash
_now=$(date +"%m_%d_%Y")
_file="/data/memeinvestor/backups/backup_$_now.sql"
echo "Starting backup to $_file..."
docker-compose run --rm mysql mysqldump DATABASE_NAME -h HOST_NAME -P PORT -u USERNAME -p -f "$_file"
