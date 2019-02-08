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


# How to deploy

On lnx004.abl.grp :

- stop Odoo stack:

```
docker stack rm odoo
```

- Edit file /srv/ABL-odoo-production/docker-compose.yml and adapt with image.

On lnx005.abl.grp :

- do a database backup:

```
pg_dump -h lnx005.abl.grp --username=odoo-prod --password -d odoo-prod --no-owner> /mnt/linuxbackup/odoo/odoo-prod-2018-12-04-14-37.sql
```
 
On lnx004.abl.grp :

- Once the backup is done, we restart the odoo stack:

```
docker stack deploy --with-registry-auth -c /srv/ABL-odoo-production/docker-compose.yml odoo
```

Note: make sure you have access to dockerhub, you might need to do a `docker login`

In order to follow the logs during the deployment of a new release you need to search for the service:

```
camptocamp@LNX001:~$ docker service ls
ID                  NAME                      MODE                REPLICAS            IMAGE                              PORTS
3vt3mb90gc32        cups_cups                 replicated          1/1                 cardonaje/cups:latest              *:631->631/tcp, *:631->631/udp
nzdzf30ce1cw        journalbeat_journalbeat   global              1/1                 nicolaka/journalbeat:latest        
89k2b8vbovyw        odoo_mailhog              replicated          1/1                 mailhog/mailhog:latest             
j6a2hkdr0frs        odoo_odoo                 replicated          1/1                 camptocamp/alcyon_odoo:10.30.20b   
0t0isxmnkar6        odoo_odooqueuejob         replicated          1/1                 camptocamp/alcyon_odoo:10.30.20b   
46fxjuzjykzz        proftpd_proftpd           replicated          1/1                 cardonaje/proftpd:1.3.5e-1build1   *:23->23/tcp
nabye48r971m        traefik_traefik           global              1/1                 traefik:v1.7.8
```

Here we see the 2 containers `odoo_odoo` and `odoo_queuejob`, this is a gamble to get the right ID.
One of the two will be doing the marabunta steps and the other will be waiting. Thus if you see the message: "A concurrent process is already running the migration" just try to follow the other container.

With the service ID in hand do the following:

```
docker service logs -f j6a2hkdr0frs
```
