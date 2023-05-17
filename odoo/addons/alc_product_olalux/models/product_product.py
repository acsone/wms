# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.product.models.product_product import ProductProduct as Productbase


class ProductProduct(Productbase):
    def get_olalux_products_domain(self):
        """Return an additional domain (used by the method search on.

        product.product) for the wholesaler Olalux.

        Olalux can only have an access to following products:
        - All products from Royal Canin, Hill's and Nestle
        - Only food from V.M.D Aliments and DECHRA * (60422)
        - Only food and parapharmacie from VIRBAC Belgium
        and VIRBAC Belgium aliments
        """

        ##########################
        # All products suppliers #
        ##########################
        # 78650: Royal Canin
        # 68250: Hill's
        # 61800: Nestle
        all_products_supplier = self.env["res.partner"].search(
            [("is_supplier", "=", True), ("ref", "in", ["78650", "68250", "61800"])]
        )

        #######################
        # only food suppliers #
        #######################
        # Dechra: 60422
        # V.M.D. Aliment: 82702
        only_food_suppliers = self.env["res.partner"].search(
            [("is_supplier", "=", True), ("ref", "in", ["60422", "82702"])]
        )

        #######################
        # specific for Virbac #
        #######################
        # Virbac Belgium: 81200
        # Virbac Belgium Aliment: 81201
        virbac_suppliers = self.env["res.partner"].search(
            [("is_supplier", "=", True), ("ref", "in", ["81200", "81201"])]
        )

        categ_ali = self.env.ref("alc_product_food.product_categ_ali")
        categ_parapharmacie = self.env.ref(
            "alc_product_category_data.product_categ_parapharmacie"
        )

        domain = [
            "|",
            ("supplier_id", "in", all_products_supplier.ids),
            "|",
            "&",
            ("supplier_id", "in", only_food_suppliers.ids),
            ("categ_id", "child_of", categ_ali.id),
            "&",
            ("supplier_id", "in", virbac_suppliers.ids),
            "|",
            ("categ_id", "child_of", categ_ali.id),
            ("categ_id", "child_of", categ_parapharmacie.id),
        ]

        return domain
