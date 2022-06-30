FROM bitnami/postgresql:14.4.0-debian-11-r3

USER 0
RUN apt update -y && apt-get install -y wget
WORKDIR /app
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc
RUN chmod +x mc
RUN ln -s /app/mc /usr/bin/mc

COPY . .
RUN chmod +x *.sh
RUN ln -s /app/backup.sh /usr/bin/backup
RUN ln -s /app/restore.sh /usr/bin/restore
RUN ln -s /app/check_restore.sh /usr/bin/check_restore

ENTRYPOINT ["/bin/bash","-c"]
