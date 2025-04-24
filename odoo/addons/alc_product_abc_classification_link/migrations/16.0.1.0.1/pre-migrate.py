# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "Ensures the field `abc_storage` matches the first element of the field `abc_classification_product_level_ids` on product templates."
    )
    env = api.Environment(cr, SUPERUSER_ID, {})
    templates = env["product.template"].search([])
    for template in templates:
        if template.abc_classification_product_level_ids:
            template.abc_storage = template.abc_classification_product_level_ids[
                0
            ].level_id.name
        else:
            template.abc_storage = "b"
