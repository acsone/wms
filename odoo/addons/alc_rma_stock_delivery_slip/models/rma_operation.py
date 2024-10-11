# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.rma.models.rma_operation import RmaOperation as RmaOperationBase


class RmaOperation(RmaOperationBase):
    no_csv_delivery_slip = fields.Boolean(
        string="No CSV Delivery Slip",
        help="If checked, the CSV delivery slip will not be sent for this operation.",
    )
    no_entry_register_at_reception = fields.Boolean(
        help="If checked, the entry register will not be add to the reception document."
    )
    no_entry_register_at_delivery = fields.Boolean(
        help="If checked, the entry register will not be add to the delivery document."
    )
