# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.rma.models.rma_operation import RmaOperation as RmaOperationBase
from odoo.addons.stock.models.stock_location import Location


class RmaOperation(RmaOperationBase):

    return_location_id = fields.Many2one[Location]()
