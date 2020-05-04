# -*- coding: utf-8 -*-
# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    turnover = fields.Monetary("Turnover", readonly=True)
    turnover_average = fields.Monetary("Turnover average", readonly=True)
    turnover_nbr_lines = fields.Integer("Turnover (nbr lines)", readonly=True)
    turnover_average_nbr_lines = fields.Integer(
        "Turnover average (nbr lines)", readonly=True
    )
    abc_id = fields.Many2one("code.abc", string="ABC", readonly=True)
    business_unit_id = fields.Many2one(
        "product.category",
        string="Business unit",
        compute="_compute_business_unit_id",
        readonly=True,
        store=True,
    )

    @api.depends("categ_id")
    def _compute_business_unit_id(self):
        business_units = self.env["product.category"].search(
            [("is_business_unit", "=", True)]
        )

        # If there is business units, we can stop this method now
        # to avoid to loop on each product for nothing
        if not business_units:
            return

        bu_by_categ = {}
        for business_unit in business_units:
            business_unit_id = business_unit.id
            bu_by_categ[business_unit_id] = business_unit_id
            children_categ_query = """
            WITH RECURSIVE tree AS (
              SELECT id, ARRAY[]::INTEGER[] AS ancestors
              FROM product_category WHERE parent_id IS NULL

              UNION ALL

              SELECT
                product_category.id,
                tree.ancestors || product_category.parent_id
              FROM product_category, tree
              WHERE product_category.parent_id = tree.id
            ) SELECT id FROM tree WHERE %s = ANY(tree.ancestors);
            """
            self.env.cr.execute(children_categ_query, (business_unit.id,))

            for categ in self.env.cr.fetchall():
                bu_by_categ[categ[0]] = business_unit_id

        for product in self:
            if not product.categ_id or product.categ_id.id not in bu_by_categ:
                product.business_unit_id = None
            else:
                product.business_unit_id = bu_by_categ[product.categ_id.id]

    @api.model
    def compute_turnover_by_product(self):
        """
        Compute the turnover for each products, for each business unit and
        the global turnover
        :return:
        """
        config_param = self.env["ir.config_parameter"]
        turnover_delay = int(config_param.get_param("abc.turnover_delay", 0))

        #####################################
        # Compute turnover by Business Unit #
        #####################################
        turnover_by_bu_query = """
        SELECT
          bu.id,
          sum(line.price_subtotal),
          count(*)
        FROM account_invoice_line AS line
          INNER JOIN product_product AS product ON line.product_id = product.id
          INNER JOIN product_category AS bu ON product.business_unit_id = bu.id
        WHERE line.create_date > NOW() - INTERVAL '%s months'
        GROUP BY bu.id;
        """
        self.env.cr.execute(turnover_by_bu_query, (turnover_delay,))
        business_unit_obj = self.env["product.category"]

        turnover_by_bu = {}
        for line in self.env.cr.fetchall():
            bu = business_unit_obj.browse(line[0])
            bu.turnover = line[1]
            turnover_by_bu[line[0]] = (line[1], line[2])

        ################################
        # Compute turnover by products #
        ################################
        turnover_by_products_query = """
        SELECT
          line.product_id,
          product.business_unit_id,
          sum(line.price_subtotal),
          count(*)
        FROM account_invoice_line AS line
          INNER JOIN product_product AS product
          ON line.product_id = product.id
        WHERE line.create_date > NOW() - INTERVAL '%s months'
        GROUP BY product.business_unit_id, line.product_id;
        """
        self.env.cr.execute(turnover_by_products_query, (turnover_delay,))
        turnover_by_products = {}
        for result in self.env.cr.fetchall():
            turnover_by_products[result[0]] = [result[1], result[2], result[3]]

        # Compute the turnover for all products
        products = self.env["product.product"].search([])
        for product in products:
            if product.id not in turnover_by_products:
                product_turnover_sum = nbr_lines = 0
                turnover_average = turnover_average_nbr_lines = 0
            else:
                bu_id, product_turnover_sum, nbr_lines = turnover_by_products[
                    product.id
                ]

                if bu_id in turnover_by_bu:
                    bu_turnover, bu_turnover_nbr_lines = turnover_by_bu[bu_id]
                    turnover_average = (bu_turnover / 100) * product_turnover_sum
                    turnover_average_nbr_lines = (
                        bu_turnover_nbr_lines / 100
                    ) * nbr_lines
                else:
                    turnover_average = turnover_average_nbr_lines = 0

            product.write(
                {
                    "turnover": product_turnover_sum,
                    "turnover_nbr_lines": nbr_lines,
                    "turnover_average": turnover_average,
                    "turnover_average_nbr_lines": turnover_average_nbr_lines,
                }
            )

    @api.model
    def compute_abc_rate(self):
        """
        This method will compute the ABC rate for each products.
        For more information about the ABC method:
        https://en.wikipedia.org/wiki/Activity-based_costing

        The idea is to compute this rate according the turnover
        by business unit of all products on one year
        (method compute_turnover_by_product)

        The ABC method is computed according several rates.
        Normally there are three rates A, B and C
        For example, the rate A can be 80%. This rate will contain
        all products where the sum of all CA is less or equal
        than 80% of the total turnover.
        :return:
        """
        product_obj = self.env["product.product"]

        abc_rates = self.env["code.abc"].search([])

        if not abc_rates:
            raise UserError(_("Please define a least one ABC rate"))

        # We want to recompute the ABC code for all products
        # Products without invoices or deactivated products must be have
        # an empty ABC code
        remove_abc_query = "UPDATE product_product SET abc_id = NULL;"
        self.env.cr.execute(remove_abc_query)

        self.invalidate_cache(["abc_id"])

        business_units = self.env["product.category"].search(
            [("is_business_unit", "=", True)]
        )
        for business_unit in business_units:
            bu_turnover = business_unit.turnover

            # Retrieve the first ABC rate
            abc_rates_lst = [(x.id, x.rate) for x in abc_rates]
            current_abc_id, current_abc_rate = abc_rates_lst.pop(0)
            current_abc_total_amount = (bu_turnover / 100.0) * current_abc_rate
            current_abc_product_ids = []

            # Retrieve all products ordered by Turnover
            # If there is several products with the same Turnover we need
            # to take these products in one time
            ordered_product_ids_query = """
            SELECT turnover, string_agg(id::TEXT, ',')
            FROM product_product
            WHERE active = TRUE
            AND business_unit_id = %s
            AND turnover > 0
            GROUP BY turnover
            ORDER BY turnover DESC;
            """
            total_turnover_amount = 0.0
            self.env.cr.execute(ordered_product_ids_query, (business_unit.id,))
            product_ids_ordered_by_turnover = self.env.cr.fetchall()
            while product_ids_ordered_by_turnover:
                # If it is the last abc rate we don't need to compute the rest
                # We can stop the process here and set the current abc rate
                # to the rest of products.
                if not abc_rates_lst:
                    product_remaining_ids = []
                    for x in product_ids_ordered_by_turnover:
                        product_remaining_ids += [int(y) for y in x[1].split(",")]

                    products = product_obj.browse(product_remaining_ids)
                    products.write({"abc_id": current_abc_id})
                    break

                # Pop the product Turnover and the list of products
                product_turnover, product_ids_str = product_ids_ordered_by_turnover.pop(
                    0
                )
                product_ids = [int(y) for y in product_ids_str.split(",")]

                # Add these products ids in the list to update
                current_abc_product_ids += product_ids
                # Input the total Turnover amount
                total_turnover_amount += product_turnover * len(product_ids)

                # If the total Turnover amount is greater or equal than
                # the total amount of the current rate it means
                # that we need to the next rate.
                if total_turnover_amount >= current_abc_total_amount:
                    products = product_obj.browse(current_abc_product_ids)
                    products.write({"abc_id": current_abc_id})

                    # Switch to the next ABC rate and recompute
                    # the current rate
                    current_abc_id, current_abc_rate = abc_rates_lst.pop(0)
                    current_abc_total_amount = (bu_turnover / 100.0) * current_abc_rate
                    current_abc_product_ids = []

                    # If the new ABC rate is the last we continue the loop
                    # We don't need to check the next ABC rate
                    if not abc_rates_lst:
                        continue

                    # We need to check the next ABC rate to be sure that
                    # the next ABC rate is not lower than the current turnover.
                    # In some extremely rare case a ABC rate can be skipped
                    # Eg:
                    # Rate A: 40€
                    # Rate B: 70€
                    # Rate C: 100€
                    # We have two products (Product 1 with total
                    # Turnover to 75€ and product 2 with total Turnover to 10€)
                    # The product 1 should have the rate A and the product 2
                    # should have the rate C (and not B !!!)
                    while current_abc_total_amount <= total_turnover_amount:
                        current_abc_id, current_abc_rate = abc_rates_lst.pop(0)
                        current_abc_total_amount = (
                            bu_turnover / 100.0
                        ) * current_abc_rate
                        current_abc_product_ids = []

                        if not abc_rates_lst:
                            break

    @api.multi
    def update_abc_code(self):
        """
        This method will update the turnover by product
        and recompute the ABC code
        :return:
        """
        self.compute_turnover_by_product()
        self.compute_abc_rate()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    turnover = fields.Monetary("Turnover", readonly=True, compute="_compute_abc_values")
    turnover_average = fields.Monetary(
        "Turnover average", readonly=True, compute="_compute_abc_values"
    )
    turnover_nbr_lines = fields.Integer(
        "Turnover (nbr lines)", readonly=True, compute="_compute_abc_values"
    )
    turnover_average_nbr_lines = fields.Integer(
        "Turnover average (nbr lines)", readonly=True, compute="_compute_abc_values"
    )
    abc_id = fields.Many2one(
        "code.abc", string="ABC", readonly=True, compute="_compute_abc_values"
    )
    business_unit_id = fields.Many2one(
        "product.category",
        string="Business unit",
        compute="_compute_abc_values",
        readonly=True,
    )

    @api.multi
    def _compute_abc_values(self):
        for product in self:
            if len(product.product_variant_ids) != 1:
                continue

            variant = product.product_variant_ids
            product.update(
                {
                    "turnover": variant.turnover,
                    "turnover_average": variant.turnover_average,
                    "turnover_nbr_lines": variant.turnover_nbr_lines,
                    "turnover_average_nbr_lines": variant.turnover_average_nbr_lines,
                    "abc_id": variant.abc_id,
                    "business_unit_id": variant.business_unit_id,
                }
            )
