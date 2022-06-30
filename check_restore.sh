#!/bin/bash
BUCKET=$1
export POSTGRESQL_USERNAME=postgres
export POSTGRESQL_PASSWORD=password
export PGPASSWORD=password

mc alias set s3 $S3_DOMAIN $S3_ACCESS_KEY $S3_SECRET_KEY 1>&2
mc cp s3/$BUCKET/$BACKUP_NAME ./$BACKUP_NAME 1>&2

# run postgres
/opt/bitnami/scripts/postgresql/entrypoint.sh /opt/bitnami/scripts/postgresql/run.sh 1>&2 2>/dev/null&
echo "waiting for postgres server to start"
sleep 10
echo "postgres server started"
psql -h localhost -p 5432 -U postgres <$BACKUP_NAME 
