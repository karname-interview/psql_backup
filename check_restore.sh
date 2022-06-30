#!/bin/bash
BUCKET=$1

mc alias set s3 $S3_DOMAIN $S3_ACCESS_KEY $S3_SECRET_KEY 1>&2
mc cp s3/$BUCKET/$BACKUP_NAME ./$BACKUP_NAME 1>&2

# run postgres
/opt/bitnami/scripts/postgresql/entrypoint.sh /opt/bitnami/scripts/postgresql/run.sh&
psql -h localhost -p 5432 -U postgres <$BACKUP_NAME 
