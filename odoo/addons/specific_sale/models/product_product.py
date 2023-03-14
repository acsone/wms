# -*- coding: utf-8 -*-
# © 2017 Julien Coux (Camptocamp)
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _compute_sales_count(self):
        # rewrite of method as sale.report is very slow to load
        query = """
            SELECT
                product_id,
                sum ("sale_order_line"."product_uom_qty") AS "product_uom_qty",
                state
                FROM sale_order_line
                WHERE state in ('sale', 'done')
                    AND product_id in %s
                GROUP BY product_id, state
                """
        self._cr.execute(query, (tuple(self.ids),))

        done = {}
        for product_id, qty, state in self._cr.fetchall():
            product = self.browse(product_id)
            if state == "sale":
                product.sale_lines_count = qty
            elif state == "done":
                done[product_id] = qty
            product.sales_count = product.sale_lines_count + done.get(product_id, 0)

    # override compute of sales_count for perf..
    sales_count = fields.Integer(compute="_compute_sales_count")
    sale_lines_count = fields.Integer(compute="_compute_sales_count")

    @api.model
    def get_cnk_products_domain(self):
        """ Generate the domain to get stock with CNK product """
        domain = [("sale_ok", "=", True), ("cnk_code", "!=", False)]

        # The ESB Connector use the user Admin to execute the method
        # However, the real user id is in the context
        current_user = self.env["res.users"].search(
            [("id", "=", self.env.context.get("uid"))]
        )

        if current_user.is_for_newpharma:
            domain += self.get_newpharma_products_domain()

        return domain

    @api.model
    def get_sku_products_domain(self):
        """ Generate the domain to get stock with SKU product """
        domain = [("sale_ok", "=", True), ("default_code", "!=", False)]

        # The ESB Connector use the user Admin to execute the method
        # However, the real user id is in the context
        current_user = self.env["res.users"].search(
            [("id", "=", self.env.context.get("uid"))]
        )

        if current_user.is_for_olalux:
            domain += self.get_olalux_products_domain()

        return domain

    @api.model
    def get_newpharma_products_domain(self):
        """ Return an additional domain for the wholesaler NewPharma.

        It filters out all the products that are only for veterinary except
        for the ones in the category 'Médicaments vétérinaires Belges' and its
        children.
        """
        belgium_medoc = self.env.ref("alc_product_category_data.product_categ_vet_belges")
        laroyduro_suppliers = self.env["res.partner"].search(
            [("supplier", "=", True), ("ref", "=", "73657")]
        )

        return [
            "|",
            "|",
            ("veterinary_only", "=", False),
            ("categ_id", "child_of", belgium_medoc.id),
            ("supplier_id", "in", laroyduro_suppliers.ids),
        ]

    @api.model
    def get_olalux_products_domain(self):
        """ Return an additional domain (used by the method search on
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
            [("supplier", "=", True), ("ref", "in", ["78650", "68250", "61800"])]
        )

        #######################
        # only food suppliers #
        #######################
        # Dechra: 60422
        # V.M.D. Aliment: 82702
        only_food_suppliers = self.env["res.partner"].search(
            [("supplier", "=", True), ("ref", "in", ["60422", "82702"])]
        )

        #######################
        # specific for Virbac #
        #######################
        # Virbac Belgium: 81200
        # Virbac Belgium Aliment: 81201
        virbac_suppliers = self.env["res.partner"].search(
            [("supplier", "=", True), ("ref", "in", ["81200", "81201"])]
        )

        categ_ali = self.env.ref("alc_product_food.product_categ_ali")
        categ_parapharmacie = self.env.ref("alc_product_category_data.product_categ_parapharmacie")

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
