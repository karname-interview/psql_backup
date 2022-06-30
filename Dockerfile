FROM bitnami/postgresql:14.4.0-debian-11-r3

USER 0
WORKDIR /app
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc
RUN chmod +x mc
RUN ln -s /app/mc /usr/bin/mc

COPY --cmhod=+x backup.sh .
ENTRYPOINT ["/bin/bash"]

