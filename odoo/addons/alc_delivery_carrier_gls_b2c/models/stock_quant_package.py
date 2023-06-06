# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.delivery_carrier_label_gls.models.stock_quant_package import (
    StockQuantPackage as QuantPackage,
)


class StockQuantPackage(QuantPackage):

    b2c_ref = fields.Char(related="gls_picking_id.sale_id.b2c_ref", readonly=True)
    sale_name = fields.Char(related="gls_picking_id.sale_id.name", readonly=True)

    def _gls_prepare_shipment(self):
        res = super()._gls_prepare_shipment()
        reference = self.sale_name
        if self.b2c_ref:
            reference = f"{self.b2c_ref}-{self.sale_name}"
        res["ShipmentReference"] = [reference[:40]]
        comment = self.gls_picking_id.sale_id.partner_id.comment
        res["ShipmentUnit"][0]["Note1"] = comment[:50] if comment else ""

        return res
