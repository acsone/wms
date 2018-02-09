# Platform option

This project was intended to be run in integration and production on C2C cloud platform on the first place.
Then it has been decided to switch to an on-premise in the middle of the dev.

As the time of me writing, we still need to be able to deploy on our cloud platform.

Thus in order to support both on-premise and platform the environment variable `C2C_PLATFORM` has been added.

By default no Camptocamp Odoo platform setup will be done. To enable it set:

```
C2C_PLATFORM=True
```
