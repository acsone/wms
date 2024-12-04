# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.rma.models.rma_operation import RmaOperation as RmaOperationBase


class RmaOperation(RmaOperationBase):

    exclude_from_rma_shipment_advice = fields.Boolean(
        string="Don't Link to RMA shipment advice"
    )
