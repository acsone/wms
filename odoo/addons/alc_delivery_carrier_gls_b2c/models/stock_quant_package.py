# coding: utf-8
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    b2c_ref = fields.Char(related="gls_picking_id.sale_id.b2c_ref", readonly=True)
    sale_name = fields.Char(related="gls_picking_id.sale_id.name", readonly=True)

    def _gls_prepare_shipment(self):
        res = super(StockQuantPackage, self)._gls_prepare_shipment()
        reference = self.sale_name
        if self.b2c_ref:
            reference = "{}-{}".format(self.b2c_ref, self.sale_name)
        res["ShipmentReference"] = [reference[:40]]
        return res
