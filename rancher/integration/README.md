# Integration deployment

Be sure to download the rancher-compose CLI (bottom right of the Rancher GUI on
https://caas.camptocamp.net/env/1a9723)

## Process to deploy a new release

1. checkout the tag to deploy

  ```
  $ git checkout 9.X.Y
  ```

2. source the environment variables (password is in Lastpass: `Rancher: integration/rancher.env.gpg`)

  ```
  $ source <(gpg2 -d rancher.env.gpg)
  ```

3. stop the services

  ```
  $ rancher-compose -p qoqa-odoo-integration stop
  ```

4. drop the odoo and db services (so we clean the database and filestore)
  ```
  rancher-compose -p qoqa-odoo-integration rm db odoo --force
  ```

5. upgrade the services

  ```
  rancher-compose -p qoqa-odoo-integration up --pull --recreate --force-recreate --confirm-upgrade -d
  ```
