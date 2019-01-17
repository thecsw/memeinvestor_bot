#!/bin/bash

if [ $# -eq 0 ]; then
    echo "No arguments provided"
    exit 1
fi

echo "!!! This script will completely replace the live database with the backup file !!!"
echo "You sure you want to do this (Y/n)"
read choice
if [ "$choice" == "n" ]; then
    echo "Bye."
    exit 1
fi

echo "Moving the backup file to the container..."
docker cp $1 memeinvestor_bot_mysql_1:/tmp/
echo "Done."

echo "Restoring the database... (This may take several minutes)"
docker exec memeinvestor_bot_mysql_1 mysql mysql -u mysql -p'strongpass!word' < /tmp/$1
echo "Done."
