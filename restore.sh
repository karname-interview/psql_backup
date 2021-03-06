#!/bin/bash
DOMAIN=$1
PORT=$2
USERNAME=$3
DATABASE=$4
BUCKET=$5


# download backup file from S3 server
mc alias set s3 $S3_DOMAIN $S3_ACCESS_KEY $S3_SECRET_KEY 1>&2
mc cp s3/$BUCKET/$BACKUP_NAME ./$BACKUP_NAME 1>&2

# restoring backup
psql -h $DOMAIN -p $PORT -d $DATABASE -U $USERNAME <$BACKUP_NAME 
