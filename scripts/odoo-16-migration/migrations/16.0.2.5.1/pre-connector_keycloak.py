# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_moved_fields(
        env.cr,
        "keycloak.backend",
        [
            "name",
            "server_url",
            "client_id",
            "realm_name",
            "client_secret_key",
            "user_realm_name",
        ],
        "keycloak",
        "connector_keycloak",
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "keycloak.user",
        [
            "display_name",
            "keycloak_backend_id",
            "partner_id",
            "username",
            "keycloak_username",
            "enabled",
            "keycloak_id",
        ],
        "keycloak",
        "connector_keycloak",
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "res.partner",
        ["keycloak_user_ids"],
        "keycloak",
        "connector_keycloak",
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "keycloak.partner.wizard",
        [
            "keycloak_backend_id",
            "partner_id",
            "username",
            "password",
            "enabled",
        ],
        "keycloak",
        "connector_keycloak",
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "keycloak.user.wizard",
        [
            "keycloak_user_id",
            "password",
            "temporary",
            "type",
            "action",
        ],
        "keycloak",
        "connector_keycloak",
    )
