# On-premise setup

The integration instance is hosted by Limelogic in Alcyon buildings.

There are 2 servers which internal hostnames are:

- `lnx001.abl.grp` (Odoo integration)
- `lnx002.abl.grp` (DB integration)

- `lnx004.abl.grp` (Odoo prod)
- `lnx005.abl.grp` (DB prod)


From outside we only have access to `lnx001.abl.grp` through `pp-erp.alcyonbelux.be`.
And to `lnx004.abl.grp` through `erp.alcyonbelux.be`.

# Contacts

- jean.cardona@limelogic.be
- eric.granados@limelogic.be
- christian.lardinois@limelogic.be

To contact for SSH keys and for each new release.


# Firewall

To access `(pp-)erp.alcyonbelux.be`. You need first to go through the firewall.
By default all ports are blocked. (HTTP, HTTPS and SSH)

To unblock, simply open https://erp.alcyonbelux.be in a browser.

You will be prompted for a user and password.

    User: pp-odoo
    Password: <lastpass: "alcyonbelux.be Firewall Alcyon">

Then you will be redirected on Odoo login page.
Once done, your IP will be authorized for a couple of hours
(duration may vary based on the configuration from Limelogic)
and you will be able to access the server through SSH.

# Access Odoo

(first ensure you unlocked the firewall)

Odoo is available at https://erp.alcyonbelux.be

Login: admin
Password: <lastpass: "[odoo-test] alcyon test admin - Limelogic">

# SSH access

(first make sure you transmited your SSH key to Limelogic)
(second ensure you unlocked the firewall)

```
ssh -p 23 camptocamp@pp-erp.alcyonbelux.be
# docker-compose.yml is in:
cd /srv/ABL-odoo-preproduction/
```

# Logs

(first ensure you unlocked the firewall)

You can access logs through kibana:

http://pp-kibana.alcyonbelux.be:5601/


Example of useful filters:

```
journal.container_name: *odoo*
```

```
journal.container_name: *odoo* AND message: *ERROR*
```


# How to retrieve an integration database dump

(first ensure you unlocked the firewall)

To access database we need to make a jump through lnx001.abl.grp:

```
# Prod
ssh -p 23 camptocamp@pp-erp.alcyonbelux.be -L 5555:lnx005.abl.grp:5432
# Integration
ssh -p 23 camptocamp@pp-erp.alcyonbelux.be -L 5555:lnx002.abl.grp:5432
```

Thus, you can access to the database with:

Login: odoo-preprod
Password: <lastpass: "Alcyon odoo-preprod DB Limelogic">

```
psql -p 5555 -h localhost -U odoo-preprod odoo-preprod
```

or create your dump (you will need postgres 9.6):

```
/usr/lib/postgresql/9.6/bin/pg_dump -p 5555 -h localhost -U odoo-preprod --format=c --file /tmp/$(date -I)-erp-alcyon.pg odoo-preprod
```
The dump is already heavy. Expect a file bigger than 400 MB.


# Second temporary server

A second Odoo server is hosted on lnx001.abl.grp.
Odoo is accessible through https://temp-pp-erp.alcyonbelux.be .

This server is where we load full data from scratch and shouldn't be used.
It is a separated server as the load of data takes few days and we can't let the users
use it during that time.
