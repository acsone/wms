# Integration templates

That will change!

For now, you have to export the following variables:

```

export RANCHER_URL=https://caas.camptocamp.net
export RANCHER_ACCESS_KEY=# create an api key
export RANCHER_SECRET_KEY=# create an api key

export DB_NAME=alcyon_int
export DB_USER=odoo
export DB_PORT=5432
export DB_PASSWORD=# see in lastpass ("Alcyon Integration Postgres")
export SCENARIO_MAIN_TAG=alcyon
export ADMIN_PASSWD=# set an admin password (anything, we don't use it)
export RUNNING_ENV=integration
export DEMO=scenario
export WORKERS=4
export MAX_CRON_THREADS=2
export LOG_LEVEL=info
export LOG_HANDLER=:INFO
export DB_MAXCONN=64
export LIMIT_MEMORY_SOFT=2147483648
export LIMIT_MEMORY_HARD=2684354560
export LIMIT_REQUEST=8192
export LIMIT_TIME_CPU=86400
export LIMIT_TIME_REAL=86400

```

The command to start the stack is 

```
rancher-compose -p alcyon-odoo-integration up -d
```

## Process to setup the integration server:

Things to check:

* you are in the correct version (`git checkout <tag>`)
* In `docker-compose.yml`, verify that the tag of the image is the correct one
  (such as camptocamp/alcyon_odoo:9.0.0)

1. source the variables above
2. stop and drop the services if they are running

  ```
  rancher-compose -p alcyon-odoo-integration rm --force
  ```

3. start the new stack

  ```
  rancher-compose -p alcyon-odoo-integration up --pull --recreate --force-recreate --confirm-upgrade -d
  ```
