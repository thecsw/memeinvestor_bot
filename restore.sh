#!/bin/bash

if [ $# -eq 0 ]; then
    echo "No arguments provided"
    exit 1
fi

if [ ! -e $1 ]; then
    echo "File does not exist"
    exit 1
fi

echo "Do you want to proceed? (Y/n)"
read choice
if [ "$choice" == "n" ]; then
    echo "Bye."
    exit 1
fi

echo "Moving the backup file to the container..."
docker cp $1 memeinvestor_bot_mysql_1:/tmp/
echo "Done."

echo "Restoring the database... (This may take several minutes)"
echo "mysql mysql -u mysql -p'strongpass!word' < /tmp/$1" | docker exec -i memeinvestor_bot_mysql_1 bash
echo "Done."
