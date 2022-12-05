# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    supplier_promotion_ids = fields.One2many(
        "product.supplierinfo", compute="_compute_seller_ids_subfields"
    )
    supplier_promotion_for_veterinaries_ids = fields.One2many(
        "product.supplierinfo", compute="_compute_seller_ids_subfields"
    )
    supplier_discount_ids = fields.One2many(
        "product.supplierinfo", compute="_compute_seller_ids_subfields"
    )

    supplier_promotion_json = fields.Serialized(compute="_compute_seller_ids_jsons")
    supplier_promotion_json_for_veterinaries = fields.Serialized(
        compute="_compute_seller_ids_jsons"
    )
    supplier_discount_json = fields.Serialized(compute="_compute_seller_ids_jsons")

    @api.depends(
        "seller_ids",
        "seller_ids.ratio_main_product",
        "seller_ids.discount_sale",
        "seller_ids.only_for_veterinaries",
    )
    def _compute_seller_ids_jsons(self):
        for product in self:
            product.supplier_promotion_json = []
            product.supplier_promotion_json_for_veterinaries = []
            product.supplier_discount_json = []
            current_info = product.seller_ids.filtered(lambda si: not si.is_past)
            for info in current_info:
                info_json = {
                    "date_start": info.date_start,
                    "date_end": info.date_end,
                    "time_frame": {"gte": info.date_start, "lte": info.date_end},
                }
                if info.is_promotion:
                    info_json["ratio_main_product"] = info.ratio_main_product
                    info_json[
                        "ratio_promotional_product"
                    ] = info.ratio_promotional_product
                    if info.only_for_veterinaries:
                        product.supplier_promotion_json_for_veterinaries.append(
                            info_json
                        )
                    else:
                        product.supplier_promotion_json.append(info_json)
                elif info.is_sale_discount:
                    info_json["discount_sale"] = info.discount_sale
                    product.supplier_discount_json.append(info_json)

    @api.depends("seller_ids")
    def _compute_seller_ids_subfields(self):
        for product in self:
            current_info = product.seller_ids.filtered(lambda si: not si.is_past)
            product.supplier_promotion_ids = current_info.filtered(
                lambda a: a.is_promotion and not a.only_for_veterinaries
            )
            product.supplier_promotion_for_veterinaries_ids = current_info.filtered(
                lambda a: a.is_promotion and not a.only_for_veterinaries
            )
            product.supplier_discount_ids = current_info.filtered("is_sale_discount")
