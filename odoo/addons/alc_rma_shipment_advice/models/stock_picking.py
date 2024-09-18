# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.shipment_advice.models.shipment_advice import ShipmentAdvice
from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):

    _inherit = "stock.picking"

    is_rma = fields.Boolean(related="picking_type_id.is_rma")
    rma_shipment_advice_id = fields.Many2one[ShipmentAdvice](
        string="RMA Shipment Advice",
        readonly=True,
        help="Links this picking to a Shipment Advice, allowing the transporter to"
        "collect returned products when delivering to the customer.",
    )
