#!/bin/bash -e

function deploy {
    local stack_name=$1

    wget -O - https://releases.rancher.com/compose/v0.12.1/rancher-compose-linux-amd64-v0.12.1.tar.gz |\
        tar -x -z -C ${HOME} && mv ${HOME}/rancher-compose*/rancher-compose ${HOME}/ || exit $?

    RANCHER_COMPOSE="${HOME}/rancher-compose"
    TEMPLATE_DIR="${TRAVIS_BUILD_DIR}/rancher/${stack_name}"

    source <(echo $rancher_env_password | gpg --passphrase-fd 0 --decrypt --no-tty $TEMPLATE_DIR/rancher.env.gpg)
    source $TEMPLATE_DIR/rancher.public.env

    (cd "${TEMPLATE_DIR}" && \
     ${RANCHER_COMPOSE} -p "${stack_name}" rm odoo db --force && \
     sleep 30 && \
     ${RANCHER_COMPOSE} -p "${stack_name}" up --pull --recreate --force-recreate --confirm-upgrade -d)
}

if [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
  docker login --username="$DOCKER_USERNAME" --password="$DOCKER_PASSWORD"

  if [ "$TRAVIS_BRANCH" == "master" ]; then
    echo "Deploying image to docker hub for master (latest)"
    docker tag alcyon_odoo camptocamp/alcyon_odoo:latest
    docker push "camptocamp/alcyon_odoo:latest"
    echo "Building test server"
    deploy $RANCHER_STACK_NAME
  elif [ ! -z "$TRAVIS_TAG" ]; then
    echo "Deploying image to docker hub for tag ${TRAVIS_TAG}"
    docker tag alcyon_odoo camptocamp/alcyon_odoo:${TRAVIS_TAG}
    docker push "camptocamp/alcyon_odoo:${TRAVIS_TAG}"
  elif [ ! -z "$TRAVIS_BRANCH" ]; then
    echo "Deploying image to docker hub for branch ${TRAVIS_BRANCH}"
    docker tag alcyon_odoo camptocamp/alcyon_odoo:${TRAVIS_BRANCH}
    docker push "camptocamp/alcyon_odoo:${TRAVIS_BRANCH}"
  else
    echo "Not deploying image"
  fi
fi
