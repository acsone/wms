# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # TO BE REMOVED, ONLY USED by website purchase...

    unit_in_pallet = fields.Integer(
        "Unit in pallet", compute="_compute_unit_in_package"
    )
    unit_in_box = fields.Integer("Unit in box", compute="_compute_unit_in_package")
    unit_in_shrink_wrap = fields.Integer(
        "Unit in shrink-wrap", compute="_compute_unit_in_package"
    )

    @api.depends(
        "packaging_ids", "packaging_ids.qty", "packaging_ids.packaging_type_id"
    )
    def _compute_unit_in_package(self):
        type_pallet = self.env.ref(
            "alc_product_packaging.product_packaging_type_palette"
        )
        type_box = self.env.ref("alc_product_packaging.product_packaging_type_box")
        type_wrap = self.env.ref(
            "alc_product_packaging.product_packaging_type_shrink_wrap"
        )
        for record in self:
            for pack in record.packaging_ids:
                if pack.packaging_type_id == type_pallet:
                    record.unit_in_pallet = pack.qty
                elif pack.packaging_type_id == type_box:
                    record.unit_in_box = pack.qty
                elif pack.packaging_type_id == type_wrap:
                    record.unit_in_shrink_wrap = pack.qty
