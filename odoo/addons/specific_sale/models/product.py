# -*- coding: utf-8 -*-
# © 2017 Julien Coux (Camptocamp)
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _sales_count(self):
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

    sale_lines_count = fields.Integer(compute="_sales_count")

    older_lot_id = fields.Many2one(
        "stock.production.lot", string="Older lot", compute="_compute_older_lot_id"
    )

    def _compute_older_lot_id(self):
        """Find the active lot with the oldest expirtation date.

        The lot must be in a physical location, not scraped not reserved and still have
        some quantity.

        ToDo:
        When called with multiple product the query could be improved,
        See this comment :
        github.com/camptocamp/alcyon_odoo/pull/1515#discussion_r302508955

        """
        location_physical = self.env.ref("specific_base.stock_location_vlb")
        get_lot_query = """
        SELECT lot.id
        FROM stock_production_lot AS lot
        WHERE lot.product_id = %s
        AND EXISTS (
            SELECT 1 FROM stock_quant AS quant
                LEFT JOIN stock_location AS location
                    ON quant.location_id = location.id
                WHERE quant.lot_id = lot.id AND
                      location.parent_left > {} AND
                      location.parent_right < {} AND
                      location.scrap_location = FALSE AND
                      quant.reservation_id is null AND
                      quant.qty > 0)
        ORDER BY lot.life_date
        LIMIT 1;
        """.format(
            location_physical.parent_left, location_physical.parent_right
        )
        for product in self:
            self.env.cr.execute(get_lot_query, (product.id,))
            result = self.env.cr.fetchone()
            if result:
                product.older_lot_id = result[0]
            else:
                product.older_lot_id = None

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
        belgium_medoc = self.env.ref("specific_data.product_categ_vet_belges")
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

        categ_ali = self.env.ref("specific_data.product_categ_ali")
        categ_parapharmacie = self.env.ref("specific_data.product_categ_parapharmacie")

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

    @api.multi
    def _compute_available_quantities_dict(self):
        """change the way immediately_useable_qty is computed by:
        * deducing the quants in the loss stock location (ruptures)
        * adding the quantities of moves with a lower priority or same
          priority but later date
        """
        res = super(ProductProduct, self)._compute_available_quantities_dict()
        prio = self.env.context.get("prio")
        date = self.env.context.get("date")
        corrections = {}
        loc_loss = self.env.ref("stock_lot_loss.stock_location_14019")
        loc_loss_qty = self.with_context(location=loc_loss.id)._product_available()
        exclude_location_ids = (
            self.env["stock.location"]
            .search([("exclude_from_immediately_usable_qty", "=", True)])
            .ids
        )
        exclude_qty = None
        if len(exclude_location_ids):
            exclude_qty = self.with_context(
                location=exclude_location_ids
            )._product_available()

        if prio is not None and date is not None:
            dom_quant_loc, dom_move_in_loc, dom_move_out_loc = (
                self._get_domain_locations()
            )
            domain = dom_move_out_loc + [
                # We never want to overwrite a move,
                # which ends in the loss location. The quantity isn't usable
                # and would have to be deducted in the end anyway.
                ("product_id", "in", self.ids),
                ("state", "not in", ("done", "cancel")),
                "|",
                ("priority", "<", prio),
                "&",
                ("priority", "=", prio),
                ("date", ">", date),
            ]
            move_groupby = self.env["stock.move"].read_group(
                domain, ["product_id", "product_qty"], ["product_id"], orderby="id"
            )
            for group in move_groupby:
                corrections[group["product_id"][0]] = group["product_qty"]

        for product_id in res:
            deducted_amounts = 0.0
            deducted_amounts += loc_loss_qty[product_id]["incoming_qty"]
            deducted_amounts += loc_loss_qty[product_id]["qty_available"]
            if exclude_qty:
                deducted_amounts += exclude_qty[product_id]["qty_available"]

            res[product_id]["immediately_usable_qty"] += (
                corrections.get(product_id, 0) - deducted_amounts
            )
        return res

    @api.depends("virtual_available", "incoming_qty")
    def _compute_available_quantities(self):
        super(ProductProduct, self)._compute_available_quantities()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_lines_count = fields.Integer(compute="_compute_sale_lines_count")

    lot_ids = fields.Many2many(
        "stock.production.lot", string="Lots", compute="_compute_lot_ids", readonly=True
    )

    def _compute_lot_ids(self):
        StockProductionLot = self.env["stock.production.lot"]

        for product_tmpl in self:
            products = product_tmpl.product_variant_ids
            lots = StockProductionLot.search(
                [("product_id", "in", products.ids), ("is_archived", "=", False)],
                order="life_date",
            )
            product_tmpl.lot_ids = [(6, 0, lots.ids)]

    @api.multi
    @api.depends("product_variant_ids.sales_count")
    def _compute_sale_lines_count(self):
        for product in self:
            product.sale_lines_count = sum(
                [p.sale_lines_count for p in product.product_variant_ids]
            )

    @api.multi
    def action_view_sale_lines_unavailable(self):
        self.ensure_one()

        action_data = self.env.ref(
            "specific_sale.action_sale_lines_unavailable_list"
        ).read()[0]
        action_data["domain"] = [
            ("state", "in", ["sale"]),
            ("product_id.product_tmpl_id", "=", self.id),
        ]

        return action_data

    @api.multi
    def action_view_sales(self):
        res = super(ProductTemplate, self).action_view_sales()
        if res["context"]:
            action_context = ast.literal_eval(res["context"])
            action_context["search_default_remains_to_deliver"] = 1
            res["context"] = str(action_context)
        else:
            res["context"] = "{" "'search_default_remains_to_deliver': 1," "}"
        return res
