# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _initialize_partner_b2c_client(env):
    _logger.info("Initialize b2c client on partners")
    client_codes = ["chronovet", "clubvetShop", "logiweb", "placedesvetos"]
    for client_code in client_codes:
        client = env["alc.b2c.client"].search(
            [("sale_channel_id.code", "=", client_code)]
        )
        assert client
        partners = env["res.partner"].search([("ref", "like", client_code)])
        partners.alc_b2c_client_id = client


@openupgrade.migrate()
def migrate(env, version):
    _initialize_partner_b2c_client(env)
