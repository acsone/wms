# Small container that opens a SSH connection and forward the port externally
# so we can reach the DB2 host from the Odoo container
#
# Image manually pushed on camptocamp/alcyon_pissh
#
# docker-compose configuration example:
# pissh:
#   image: camptocamp/alcyon_pissh
#   command: "ssh pi@194.78.105.88 -L 0.0.0.0:8471:10.2.2.3:8471 -N"
#   environment:
#     SSH_ID_RSA: |
#       -----BEGIN RSA PRIVATE KEY-----
#       ....
#       -----END RSA PRIVATE KEY-----
#
# With this configuration, odoo can access to DB2 on 'pissh:8471'

FROM debian

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get -y install ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY ssh_config /root/.ssh/config
RUN chmod 600 /root/.ssh/config

ENTRYPOINT ["/docker-entrypoint.sh"]
