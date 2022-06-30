#!/bin/bash
DOMAIN=$1
PORT=$2
USERNAME=$3
DATABASE=$4
NAME=$5
$BUCKET=$6

BACKUP_NAME=${NAME}_`date +"%m-%d-%y_%H-%M-%S_%s"`.sql
pg_dump -h $DOMAIN -p $PORT -d $DATABASE -U $USER > $BACKUP_NAME 

mc alias set s3 $S3_DOMAIN $S3_ACCESS_KEY $S3_SECRET_KEY 1>&2
mc mb s3/$BUCKET 1>&2
mc cp $BACKUP_NAME s3/$BUCKET 1>&2

# jason format output
echo "{ \"name\": \"$BACKUP_NAME\"}" 1>&2
echo "{ \"name\": \"$BACKUP_NAME\"}"
