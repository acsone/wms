-- Revert a few thing that the Odoo neutralization scripts did and we don't want.

\set ON_ERROR_STOP

-- we use mail_environment
DELETE FROM ir_mail_server WHERE name like 'neutralization%';
UPDATE ir_mail_server SET active=TRUE;
DELETE FROM keycloak_user where id <> 1;
UPDATE keycloak_user SET username='acsone', keycloak_username='acsone' where id=1;
