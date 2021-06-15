# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def put_in_pack(self):
        res = super(StockPicking, self).put_in_pack()
        final_pack_id = res["res_id"] if isinstance(res, dict) else res.id
        package = self.env["stock.quant.package"].browse(final_pack_id)
        package.packaging_id = self.env.ref(
            "delivery_carrier_label_gls.product_packaging_gls_parcel"
        )
        if (
            res
            and self.carrier_id.delivery_type == "gls"
            and "NO_GLS_SEND" not in self.env.context
        ):
            self.gls_send_shipping_package(package=package)
        return res
