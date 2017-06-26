#!/bin/bash

set -e
echo "${SSH_ID_RSA}" > /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa
exec "$@"
