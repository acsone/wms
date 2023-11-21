# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    data = [
        (
            "keycloak.keycloak_backend",
            "connector_keycloak.keycloak_backend",
        ),
    ]
    openupgrade.rename_xmlids(cr, data, allow_merge=True)
