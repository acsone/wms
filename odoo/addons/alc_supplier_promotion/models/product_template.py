# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.base_sparse_field.models.fields import Serialized
from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .product_supplierinfo import ProductSupplierInfo


class ProductTemplate(ProductTemplateBase):

    supplier_promotion_ids = fields.One2many[ProductSupplierInfo](
        compute="_compute_seller_ids_subfields"
    )
    supplier_promotion_for_veterinaries_ids = fields.One2many[ProductSupplierInfo](
        compute="_compute_seller_ids_subfields"
    )
    supplier_discount_ids = fields.One2many[ProductSupplierInfo](
        compute="_compute_seller_ids_subfields"
    )

    supplier_promotion_json = Serialized(compute="_compute_seller_ids_jsons")
    supplier_promotion_json_for_veterinaries = fields.Serialized(
        compute="_compute_seller_ids_jsons"
    )
    supplier_discount_json = Serialized(compute="_compute_seller_ids_jsons")
    supplier_discount_json_for_veterinaries = fields.Serialized(
        compute="_compute_seller_ids_jsons"
    )

    @api.depends(
        "seller_ids",
        "seller_ids.ratio_main_product",
        "seller_ids.discount_sale",
        "seller_ids.only_for_veterinaries",
    )
    def _compute_seller_ids_jsons(self):
        for product in self:
            product.supplier_promotion_json = supplier_promotion_json = []
            product.supplier_promotion_json_for_veterinaries = (
                supplier_promotion_json_for_veterinaries
            ) = []
            product.supplier_discount_json = supplier_discount_json = []
            product.supplier_discount_json_for_veterinaries = (
                supplier_discount_json_for_veterinaries
            ) = []
            current_info = product.seller_ids.filtered(lambda si: not si.is_past)
            for info in current_info:
                date_start = info.date_start.isoformat() if info.date_start else None
                date_end = info.date_end.isoformat() if info.date_end else None
                info_json = {
                    "date_start": date_start,
                    "date_end": date_end,
                    "time_frame": {"gte": date_start, "lte": date_end},
                }
                if info.is_promotion:
                    info_json["ratio_main_product"] = info.ratio_main_product
                    info_json[
                        "ratio_promotional_product"
                    ] = info.ratio_promotional_product
                    if info.only_for_veterinaries:
                        supplier_promotion_json_for_veterinaries.append(info_json)
                    else:
                        supplier_promotion_json.append(info_json)
                elif info.is_sale_discount:
                    info_json["discount_sale"] = info.discount_sale
                    if info.only_for_veterinaries:
                        supplier_discount_json_for_veterinaries.append(info_json)
                    else:
                        supplier_discount_json.append(info_json)
                product.supplier_promotion_json = supplier_promotion_json
                product.supplier_promotion_json_for_veterinaries = (
                    supplier_promotion_json_for_veterinaries
                )
                product.supplier_discount_json = supplier_discount_json
                product.supplier_discount_json_for_veterinaries = (
                    supplier_discount_json_for_veterinaries
                )

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

    def get_promotional_product(self, qty, uom, partner_id):
        """Compute how many promotional product are offered.

        Given a quantity and a unity of measure, returns for the current
        day how many promotional (free) product will be given.
        The unit of measure is adapted if needs be.
        """
        self.ensure_one()
        if uom != self.uom_id:
            qty = uom._compute_quantity(qty, self.uom_id)
        domain = []
        if partner_id.partner_type != "veterinary":
            domain.append(("only_for_veterinaries", "=", False))
        domain = domain + [
            ("ratio_promotional_product", ">", 0),
            ("ratio_main_product", ">", 0),
            "|",
            ("date_start", "=", False),
            ("date_start", "<=", fields.Date.today()),
            "|",
            ("date_end", "=", False),
            ("date_end", ">=", fields.Date.today()),
            "|",
            ("min_qty_sale", "=", False),
            ("min_qty_sale", "<=", qty),
            ("product_tmpl_id", "=", self.id),
        ]
        result = self.env["product.supplierinfo"].search(
            domain,
            order="sequence, min_qty_sale desc, price",
            limit=1,
        )
        if not result:
            return 0
        coefficient = int(qty / result.ratio_main_product)
        return coefficient * result.ratio_promotional_product
