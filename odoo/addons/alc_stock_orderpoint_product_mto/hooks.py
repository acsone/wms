# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    mto_product_without_orderpoint = env["product.product"].search(
        [
            ("is_mto", "=", True),
            ("orderpoint_ids", "=", False),
            ("type", "=", "product"),
            ("sale_ok", "=", True),
        ]
    )
    _logger.info(
        "Create orderpoints for %s MTO products without orderpoint",
        len(mto_product_without_orderpoint),
    )
    mto_product_without_orderpoint._create_default_orderpoint_for_mto()
    _logger.info("Orderpoints creation finished")
