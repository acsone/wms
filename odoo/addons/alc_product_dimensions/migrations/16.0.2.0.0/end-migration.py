# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID
from odoo.api import Environment

logger = logging.getLogger(__name__)


def migrate(cr, version):
    logger.info("Recompute product and product template volume")
    env = Environment(cr, SUPERUSER_ID, {})
    for model in ("product.product", "product.template"):
        for batch in env[model].search([]).batch(1000):
            logger.info(
                f"Recompute volume for {model} for a batch of %s records", len(batch)
            )
            batch._compute_volume()
            env.cr.commit()
