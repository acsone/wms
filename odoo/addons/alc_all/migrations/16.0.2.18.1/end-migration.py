# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID
from odoo.api import Environment

logger = logging.getLogger(__name__)


def _enable_unique_partner_sequence(cr):
    env = Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].sudo().set_param(
        "base_partner_sequence.partner_generated_reference_unique", True
    )


def migrate(cr, version):
    logger.info("Disable session store on fastapi")
    cr.execute("UPDATE fastapi_endpoint set save_http_session = false")
    _enable_unique_partner_sequence(cr)
