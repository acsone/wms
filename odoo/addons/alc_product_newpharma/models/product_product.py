# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.product.models.product_product import ProductProduct as ProductBase


class ProductProduct(ProductBase):
    @api.model
    def get_newpharma_products_domain(self):
        """Return an additional domain for the wholesaler NewPharma.

        It filters out all the products that are only for veterinary except
        for the ones in the category 'Médicaments vétérinaires Belges' and its
        children.
        """
        belgium_medoc = self.env.ref(
            "alc_product_category_data.product_categ_vet_belges"
        )
        laroyduro_suppliers = self.env["res.partner"].search(
            [("is_supplier", "=", True), ("ref", "=", "73657")]
        )

        return [
            "|",
            "|",
            ("veterinary_only", "=", False),
            ("categ_id", "child_of", belgium_medoc.id),
            ("supplier_id", "in", laroyduro_suppliers.ids),
        ]
