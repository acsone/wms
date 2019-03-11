# Full Composition (Odoo, Akeneo, WSO2)

Usually we only want to run Odoo, so the main composition
(`docker-compose.yml`) file only includes Odoo and its associated services
(nginx, postgres).

But sometime we might to have the other services, the PIM Akeneo and the ESB WSO2.

# Akeneo:

For developers:

```
$ docker-compose -f docker-compose.yml -f akeneo.yml up
```

For testers:

```
$ docker-compose -f test.yml -f akeneo.yml up
```

Now, you can open a browser on http://localhost:9000.
The login is `admin / admin`.

# WSO2

For developers:

```
$ docker-compose -f docker-compose.yml -f wso2.yml up
```

For testers:

```
$ docker-compose -f test.yml -f wso2.yml up
```


Now, you can open a browser on https://localhost:9443 (you will have to accept
the unsecure connection).
The login is `admin / admin`.

# All of them:

For developers:

```
$ docker-compose -f docker-compose.yml -f akeneo.yml -f wso2.yml up
```

For testers:

```
$ docker-compose -f test.yml -f akeneo.yml -f wso2.yml up
```
