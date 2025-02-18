# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Update internal picking types sequence codes")
    env = api.Environment(cr, SUPERUSER_ID, {})
    int_type = env["stock.picking.type"].search([("sequence_code", "=", "WH/INT/")])
    int_type.sequence_code = "INT"
