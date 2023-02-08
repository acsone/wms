# Keycloak

## local setup

`docker-compose up docker-compose-keycloak.yml`

## keycloak configuration

Create `OdooAlcyonLocal` realm. In `Login` panel, deactivate `login with email` and
activate `duplicate emails`. In master realm, create `alcyon` client. Set it to
`confidential` access type, then activate `Service Accounts Enabled`. Once saved, you
can find the client secret in a new panel `Credentials`. In `Service Account Roles`
panel, assign it admin role. In the `Mappers` panel, you can now create new protocol
mappers for the added fields using a `User Attribute` type to link it to the token (e.g.
`shopinvader-vt-roles`, `supplier_id`). More details at
https://www.baeldung.com/keycloak-custom-user-attributes.

## python client

Installing python-keycloak with pip will just not work™. Future is required
(`pip install future`), as well as recent versions of `urllib3` and `requests`. Working
versions are already in the `requirements.txt` file.
https://github.com/marcospereirampj/python-keycloak/issues/196

## odoo server variables

Your `.odoorc` file should contain the following lines: (if you used defaults, only
`client_secret_key` needs to be adapted)

[keycloak_backend.Default] server_url=http://localhost:8080/auth/ client_id=alcyon
client_secret_key=c822680e-given-by-your-instance username=admin password=admin
realm_name=OdooAlcyonLocal
