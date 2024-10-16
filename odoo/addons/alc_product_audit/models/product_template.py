# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import api, fields
from odoo.osv.expression import OR

from odoo.addons.product.models.product_template import ProductTemplate as Product


class ProductTemplate(Product):

    _inherit = "product.template"

    no_min_max_no_on_command_reappro = fields.Boolean(
        default=False,
        compute="_compute_min_max_and_on_command_reappro",
        store=True,
        index=True,
    )
    min_max_on_command_reappro = fields.Boolean(
        default=False,
        compute="_compute_min_max_and_on_command_reappro",
        store=True,
        index=True,
    )
    sale_not_ok_not_archived = fields.Boolean(
        default=False,
        compute="_compute_sale_not_ok_not_archived",
        store=True,
        index=True,
    )

    mismatch_route_picking = fields.Boolean(
        default=False, compute="_compute_mismatch_route_picking", store=True, index=True
    )

    mto_with_abnormal_route = fields.Boolean(
        default=False,
        compute="_compute_mto_with_abnormal_route",
        store=True,
        index=True,
    )

    can_be_bought_without_buy_route = fields.Boolean(
        default=False,
        compute="_compute_can_be_bought_without_buy_route",
        store=True,
        index=True,
    )

    mto_purchased_not_sold = fields.Boolean(
        default=False,
        compute="_compute_mto_purchased_not_sold",
        search="_search_mto_purchased_not_sold",
    )

    mto_stock_no_mto_route = fields.Boolean(
        default=False,
        compute="_compute_mto_stock_no_mto_route",
        search="_search_mto_stock_no_mto_route",
    )

    mto_stock_new_route = fields.Boolean(
        default=False,
        compute="_compute_mto_stock_new_route",
        search="_search_mto_stock_new_route",
    )

    mto_stock_5_days = fields.Boolean(
        default=False,
        compute="_compute_mto_stock_5_days",
        search="_search_mto_stock_5_days",
    )

    not_sold_on_website = fields.Boolean(
        default=False,
        compute="_compute_not_sold_on_website",
        store=True,
        index=True,
    )

    no_dimensions_in_stock = fields.Boolean(
        default=False,
        compute="_compute_no_dimensions_in_stock",
        search="_search_no_dimensions_in_stock",
    )

    dimensions_in_stock = fields.Boolean(
        default=False,
        compute="_compute_dimensions_in_stock",
        search="_search_dimensions_in_stock",
    )

    has_anomaly = fields.Boolean(
        default=False, compute="_compute_has_anomaly", search="_search_has_anomaly"
    )

    @api.depends("route_ids", "orderpoint_min", "orderpoint_max")
    def _compute_min_max_and_on_command_reappro(self):
        on_command_reappro_route = self.env.ref("stock.route_warehouse0_mto")
        for product in self:
            if product.type == "service":
                # No min/max or reappro rule on services
                continue

            if (
                not product.orderpoint_min
                and not product.orderpoint_max
                and on_command_reappro_route not in product.route_ids
            ):
                product.no_min_max_no_on_command_reappro = True
            else:
                product.no_min_max_no_on_command_reappro = False

            if (
                product.orderpoint_min
                and product.orderpoint_max
                and on_command_reappro_route in product.route_ids
            ):
                product.min_max_on_command_reappro = True
            else:
                product.min_max_on_command_reappro = False

    @api.depends("sale_ok", "active")
    def _compute_sale_not_ok_not_archived(self):
        for product in self:
            if not product.sale_ok and product.active:
                product.sale_not_ok_not_archived = True
            else:
                product.sale_not_ok_not_archived = False

    @api.depends("purchase_ok", "route_ids")
    def _compute_can_be_bought_without_buy_route(self):
        purchase_route = self.env.ref("purchase_stock.route_warehouse0_buy")
        for product in self:
            product_routes = product.route_ids
            if product.purchase_ok and purchase_route not in product_routes:
                product.can_be_bought_without_buy_route = True
            else:
                product.can_be_bought_without_buy_route = False

    @api.depends("route_ids")
    def _compute_mismatch_route_picking(self):
        Rule = self.env["stock.rule"]
        stock_location = self.env.ref("stock.stock_location_stock")
        picking_types = self.env["stock.picking.type"].search(
            [("default_location_src_id", "child_of", stock_location.id)]
        )
        for product in self:
            product_routes = product.route_ids

            res = Rule.search(
                [
                    ("route_id", "in", product_routes.ids),
                    ("picking_type_id", "in", picking_types.ids),
                ],
                order="route_sequence, sequence",
            )
            if len(res) > 1:
                product.mismatch_route_picking = True
            else:
                product.mismatch_route_picking = False

    @api.depends("route_ids")
    def _compute_mto_with_abnormal_route(self):
        new_route = self.env.ref(
            "__setup__.stock_location_route_new", raise_if_not_found=False
        )
        for product in self:
            product_routes = product.route_ids
            if product.is_mto and new_route and new_route in product_routes:
                product.mto_with_abnormal_route = True
            else:
                product.mto_with_abnormal_route = False

    def _get_current_ids(self):
        # copied as is into alc_product_is_new to avoid the whole dependency
        if self.ids and len(self.ids) > 1:
            current_ids = AsIs(f"AND pt.id in {tuple(self.ids)}")
        elif self.ids and len(self.ids) == 1:
            current_ids = AsIs(f"AND pt.id = {self.ids[0]}")
        else:
            current_ids = AsIs("")
        return current_ids

    def _get_mto_product_without_sale_order(self):
        current_ids = self._get_current_ids()
        self.env.cr.execute(
            """
            SELECT DISTINCT pt.id
                   FROM
                        purchase_order_line pol
                   JOIN
                        product_product pp ON pp.id = pol.product_id
                   JOIN
                        product_template pt ON pt.id = pp.product_tmpl_id AND pt.is_mto = True
                   WHERE
                        pol.state NOT IN ('cancel', 'done') AND pol.product_qty - pol.qty_received > 0
                   AND NOT EXISTS
                        (
                            SELECT sol.id FROM sale_order_line sol
                                   WHERE
                                        sol.product_id = pol.product_id
                                   AND
                                        sol.product_qty_remains_to_deliver > 0
                        )
                   %(ids)s
            """,
            {"ids": current_ids},
        )
        result = self.env.cr.fetchall()
        ids = [r[0] for r in result]
        return ids

    @api.depends("is_mto", "route_ids")
    def _compute_mto_purchased_not_sold(self):
        ids_mto_purchased_not_sold = set(self._get_mto_product_without_sale_order())
        for product in self:
            product.mto_purchased_not_sold = product.id in ids_mto_purchased_not_sold

    def _search_mto_purchased_not_sold(self, operator, value):
        ids = self._get_mto_product_without_sale_order()
        return [("id", "in", ids)]

    def _get_mto_stock_no_mto_route(self):
        stock_location_mto = self.env.ref(
            "__setup__.stock_location_onorder", raise_if_not_found=False
        )
        ids = []
        current_ids = self._get_current_ids()

        if stock_location_mto:
            self.env.cr.execute(
                """
                SELECT DISTINCT pt.id
                    FROM
                            stock_quant sq
                    JOIN
                            stock_location sl ON sl.id = sq.location_id
                    JOIN
                            product_product pp ON pp.id = sq.product_id
                    JOIN
                            product_template pt ON pt.id = pp.product_tmpl_id AND pt.is_mto = False
                    WHERE
                            sl.location_kind = 'bin'
                            AND sl.parent_path LIKE %(stock_location_mto_parent)s || '%%'
                            AND sq.quantity > 0
                            %(ids)s
                """,
                {
                    "stock_location_mto_parent": stock_location_mto.parent_path,
                    "ids": current_ids,
                },
            )
            result = self.env.cr.fetchall()
            ids = [r[0] for r in result]

        return ids

    @api.depends("is_mto", "route_ids")
    def _compute_mto_stock_no_mto_route(self):
        ids_mto_stock_no_mto_route = set(self._get_mto_stock_no_mto_route())
        for product in self:
            product.mto_stock_no_mto_route = bool(
                product.id in ids_mto_stock_no_mto_route
            )

    def _search_mto_stock_no_mto_route(self, operator, value):
        ids = self._get_mto_stock_no_mto_route()
        return [("id", "in", ids)]

    def _get_mto_stock_new_route(self):
        ids = []
        stock_location_mto = self.env.ref(
            "__setup__.stock_location_onorder", raise_if_not_found=False
        )
        new_route = self.env.ref(
            "__setup__.stock_location_route_new", raise_if_not_found=False
        )
        current_ids = self._get_current_ids()
        if stock_location_mto:
            self.env.cr.execute(
                """
                SELECT DISTINCT pt.id
                    FROM
                            stock_quant sq
                    JOIN
                            stock_location sl ON sl.id = sq.location_id
                    JOIN
                            product_product pp ON pp.id = sq.product_id
                    JOIN
                            product_template pt ON pt.id = pp.product_tmpl_id
                    JOIN
                            stock_route_product srp ON pt.id = srp.product_id
                    WHERE
                            sl.location_kind = 'bin'
                    AND sl.parent_path LIKE %(stock_location_mto_parent)s || '%%'
                    AND sl.parent_path != %(stock_location_mto_parent)s
                    AND sq.quantity > 0
                    AND srp.route_id = %(new_route_id)s
                    %(ids)s
                """,
                {
                    "stock_location_mto_parent": stock_location_mto.parent_path,
                    "new_route_id": new_route.id,
                    "ids": current_ids,
                },
            )
            result = self.env.cr.fetchall()
            ids = [r[0] for r in result]

        return ids

    @api.depends("is_mto", "route_ids")
    def _compute_mto_stock_new_route(self):
        ids_mto_stock_new_route = set(self._get_mto_stock_new_route())
        for product in self:
            product.mto_stock_new_route = product.id in ids_mto_stock_new_route

    def _search_mto_stock_new_route(self, operator, value):
        ids = self._get_mto_stock_new_route()
        return [("id", "in", ids)]

    @api.depends("sale_ok", "web_published")
    def _compute_not_sold_on_website(self):
        for product in self:
            if not product.sale_ok and product.web_published:
                product.not_sold_on_website = True
            else:
                product.not_sold_on_website = False

    def _get_mto_stock_5_days(self):
        stock_location_mto = self.env.ref(
            "__setup__.stock_location_onorder", raise_if_not_found=False
        )
        ids = []
        current_ids = self._get_current_ids()
        if stock_location_mto:
            self.env.cr.execute(
                """
                SELECT DISTINCT pt.id
                    FROM
                            stock_quant sq
                    JOIN
                            stock_location sl ON sl.id = sq.location_id
                    JOIN
                            product_product pp ON pp.id = sq.product_id
                    JOIN
                            product_template pt ON pt.id = pp.product_tmpl_id AND pt.is_mto = True
                    WHERE
                            sl.location_kind = 'bin'
                            AND sl.parent_path LIKE %(stock_location_mto_parent)s || '%%'
                            AND sq.quantity > 0
                            AND sq.write_date <  current_date - interval '5' day
                            %(ids)s
                """,
                {
                    "stock_location_mto_parent": stock_location_mto.parent_path,
                    "ids": current_ids,
                },
            )
            result = self.env.cr.fetchall()
            ids = [r[0] for r in result]

        return ids

    @api.depends("is_mto", "route_ids")
    def _compute_mto_stock_5_days(self):
        ids_mto_stock_5_days = set(self._get_mto_stock_5_days())
        for product in self:
            product.mto_stock_5_days = product.id in ids_mto_stock_5_days

    def _search_mto_stock_5_days(self, operator, value):
        ids = self._get_mto_stock_5_days()
        return [("id", "in", ids)]

    def _get_product_dimensions_in_stock(self, no_dimensions):
        ids = []
        current_ids = self._get_current_ids()
        self.env.cr.execute(
            """
            SELECT DISTINCT pt.id
                FROM
                        product_template pt
                JOIN
                        product_product pp on pp.product_tmpl_id = pt.id AND pt.is_mto = False
                JOIN
                        stock_quant sq on sq.product_id = pp.id
                JOIN
                        stock_location sl ON sl.id = sq.location_id
                WHERE
                        sq.quantity > 0
                    AND sl.location_kind = 'bin'
                    %(no_product_dimensions)s
                    %(no_packaging_dimensions)s
                    AND pt.active = True
                    AND pt.sale_ok = True
                    AND pt.type='product'
                    AND pt.is_human = False
                    %(ids)s
            """,
            {
                "no_product_dimensions": (
                    AsIs("AND pt.has_no_dimensions = True")
                    if no_dimensions
                    else AsIs("AND pt.has_no_dimensions = False")
                ),
                "no_packaging_dimensions": (
                    AsIs("OR pt.packaging_has_no_dimensions = True")
                    if no_dimensions
                    else AsIs("AND pt.packaging_has_no_dimensions = False")
                ),
                "ids": current_ids,
            },
        )
        result = self.env.cr.fetchall()
        ids = [r[0] for r in result]

        return ids

    @api.depends(
        "sale_ok",
        "active",
        "is_mto",
        "has_no_dimensions",
        "packaging_has_no_dimensions",
        "route_ids",
    )
    def _compute_no_dimensions_in_stock(self):
        ids_not_in_stock = set(
            self._get_product_dimensions_in_stock(no_dimensions=True)
        )
        for product in self:
            product.no_dimensions_in_stock = product.id in ids_not_in_stock

    def _search_no_dimensions_in_stock(self, operator, value):
        ids = self._get_product_dimensions_in_stock(no_dimensions=True)
        return [("id", "in", ids)]

    @api.depends(
        "sale_ok",
        "active",
        "is_mto",
        "has_no_dimensions",
        "packaging_has_no_dimensions",
        "route_ids",
    )
    def _compute_dimensions_in_stock(self):
        ids_in_stock = set(self._get_product_dimensions_in_stock(no_dimensions=False))
        for product in self:
            product.dimensions_in_stock = product.id in ids_in_stock

    def _search_dimensions_in_stock(self, operator, value):
        ids = self._get_product_dimensions_in_stock(no_dimensions=False)
        return [("id", "in", ids)]

    def _get_anomaly_fields(self):
        return [
            "mismatch_route_picking",
            "sale_not_ok_not_archived",
            "min_max_on_command_reappro",
            "no_min_max_no_on_command_reappro",
            "mto_with_abnormal_route",
            "can_be_bought_without_buy_route",
            "has_no_dimensions",
            "packaging_has_no_dimensions",
            "mto_purchased_not_sold",
            "mto_stock_no_mto_route",
            "mto_stock_new_route",
            "not_sold_on_website",
            "mto_stock_5_days",
            "no_dimensions_in_stock",
        ]

    @api.depends(
        "min_max_on_command_reappro",
        "no_min_max_no_on_command_reappro",
        "sale_not_ok_not_archived",
        "mismatch_route_picking",
        "mto_with_abnormal_route",
        "can_be_bought_without_buy_route",
        "has_no_dimensions",
        "packaging_has_no_dimensions",
        "mto_purchased_not_sold",
        "mto_stock_no_mto_route",
        "mto_stock_new_route",
        "not_sold_on_website",
        "mto_stock_5_days",
        "no_dimensions_in_stock",
    )
    def _compute_has_anomaly(self):
        anomalies = self._get_anomaly_fields()
        for product in self:
            product.has_anomaly = any(product[anomaly] for anomaly in anomalies)

    def _search_has_anomaly(self, operator, value):
        anomalies = self._get_anomaly_fields()
        domain = OR([[(anomaly, "=", True)] for anomaly in anomalies])

        ids_5_days = self._search_mto_stock_5_days(operator, value)
        ids_new_route = self._search_mto_stock_new_route(operator, value)
        ids_no_customer = self._search_mto_purchased_not_sold(operator, value)

        domain += [ids_5_days[0], ids_new_route[0], ids_no_customer[0]]
        return domain
