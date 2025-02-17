# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Update picking types sequence code")
    env = api.Environment(cr, SUPERUSER_ID, {})
    in_type = env["stock.picking.type"].browse([1, 8])
    in_type.sequence_code = "IN"

    pack_type = env["stock.picking.type"].browse(2)
    pack_type.sequence_code = "PACK"

    out_type = env["stock.picking.type"].browse([4, 21, 22, 27])
    out_type.sequence_code = "OUT"

    pick_type = env["stock.picking.type"].browse([3, 15, 16, 18, 24])
    pick_type.sequence_code = "PICK"
