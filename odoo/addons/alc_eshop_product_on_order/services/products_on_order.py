# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import sql
from psycopg2.extensions import AsIs
from werkzeug.exceptions import NotFound

from odoo import _

from odoo.addons.alc_cerberus_utils import utils
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component

from ..exceptions import NoBackOrderError


class ProductsOnOrderService(Component):
    """Provides services to manages products on order."""

    _inherit = "base.rest.service"
    _name = "product.on.order.service"
    _collection = "shopinvader.backend"
    _usage = "products_on_order"

    @restapi.method(
        [(["/<int:order_line_id>"], "GET")],
        output_param=restapi.CerberusValidator("_order_line_schema"),
    )
    def get(self, order_line_id):
        value = self._get(order_line_id)
        if not value:
            raise NotFound("No order line found for id %s" % order_line_id)
        return value

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search(
        self,
        page=None,
        per_page=None,
        product_families=None,
        order_ref=None,
        order_date_min=None,
        order_date_max=None,
        customer_ref=None,
        restricts=None,
    ):
        """Get products on order."""
        return self._get_search(
            page=page,
            per_page=per_page,
            product_families=product_families,
            order_ref=order_ref,
            order_date_min=order_date_min,
            order_date_max=order_date_max,
            customer_ref=customer_ref,
            restricts=restricts,
        )

    @restapi.method(
        [(["/cancel/<int:order_line_id>"], "POST")],
        input_param=restapi.CerberusValidator("_cancel_input_schema"),
        output_param=restapi.CerberusValidator("_cancel_output_schema"),
    )
    def cancel(self, order_line_id, params):
        """Request cancellation of specified order line.

        The cancellation is only possible for purchased products in back
        order
        """
        product_on_order = self.env["alc.eshop.product.on.order"].search(
            [("id", "=", order_line_id), ("partner_id", "=", self.partner.id)]
        )
        if not product_on_order.exists():
            return {
                "status": False,
                "error_msg": _("Requested order line no more exists"),
            }
        try:
            product_on_order.request_backorder_cancellation(quantity=params["quantity"])
        except NoBackOrderError as error:
            return {"status": False, "error_msg": error.message}
        return {"status": True}

    ############
    # validators
    ############
    def _search_input_schema(self):
        return {
            "page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 1,
            },
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 10,
            },
            "restricts": {"type": "list", "allowed": ["has_backorder", "is_mto"]},
            "product_families": {
                "type": "list",
                "allowed": ["meds", "food", "equipment"],
            },
            "order_ref": {"type": "string", "nullable": False},
            "customer_ref": {"type": "string", "nullable": False},
            "order_date_min": {
                "type": "datetime",
                "nullable": False,
                "coerce": utils.isoformat_str_dt_to_dt_utc,
            },
            "order_date_max": {
                "type": "datetime",
                "nullable": False,
                "coerce": utils.isoformat_str_dt_to_dt_utc,
            },
        }

    def _search_output_schema(self):
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._order_line_schema()},
            },
        }

    def _order_line_schema(self):
        return {
            "order_line_id": {
                "coerce": to_int,
                "nullable": False,
                "required": True,
                "type": "integer",
            },
            "product_id": {
                "coerce": to_int,
                "nullable": False,
                "required": True,
                "type": "integer",
            },
            "description": {"nullable": True, "required": True, "type": "string"},
            "order_ref": {"nullable": False, "required": True, "type": "string"},
            "order_date": {"nullable": False, "required": True, "type": "datetime"},
            "customer_ref": {"nullable": True, "required": False, "type": "string"},
            "qty_ordered": {"nullable": False, "required": True, "type": "float"},
            "qty_to_deliver": {"nullable": False, "required": True, "type": "float"},
            "qty_in_backorder": {"nullable": False, "required": True, "type": "float"},
            "product_family": {
                "type": "string",
                "allowed": ["meds", "food", "equipment"],
                "nullable": False,
            },
            "is_mto": {"type": "boolean", "nullable": False},
            "has_backorder": {"type": "boolean", "nullable": False},
        }

    def _cancel_input_schema(self):
        return {
            "quantity": {
                "type": "float",
                "coerce": float,
                "required": True,
                "nullable": True,
            }
        }

    def _cancel_output_schema(self):
        return {
            "status": {"type": "boolean", "required": True, "nullable": False},
            "error_msg": {
                "type": "string",
                "required": False,
                "nullable": False,
                "meta": {"description": "Error message in case of status=False "},
            },
        }

    ################
    # implementation
    ################
    @property
    def env(self):
        env = self.work.env
        return env

    @property
    def partner(self):
        partner = self.env["res.partner"].browse()
        partner_id = self.work.authenticated_partner_id
        if partner_id:
            partner = partner.browse(partner_id)
        return partner

    def _get(self, order_line_id):
        query = """
            SELECT
                *
            FROM
                %(table)s
            WHERE
                partner_id = %(partner_id)s
                AND order_line_id = %(order_line_id)s
        """
        self.env.cr.execute(
            query,
            dict(
                partner_id=self.partner.id,
                order_line_id=order_line_id,
                table=AsIs(self.env["alc.eshop.product.on.order"]._table),
            ),
        )
        row = self.env.cr.dictfetchone()
        if row:
            return self._search_row_to_json(row)
        return {}

    def _get_search(
        self,
        page=None,
        per_page=None,
        product_families=None,
        order_ref=None,
        order_date_min=None,
        order_date_max=None,
        customer_ref=None,
        restricts=None,
    ):
        where_clause, where_params = self._get_search_where_clause(
            product_families=product_families,
            order_ref=order_ref,
            order_date_min=order_date_min,
            order_date_max=order_date_max,
            customer_ref=customer_ref,
            restricts=restricts,
        )
        query = sql.SQL(
            """
    SELECT
        c.count,
        a.*
    FROM (
        (
            SELECT
                count(1)
            FROM
                %(table)s
            WHERE
                partner_id = %(partner_id)s
                {where}
        ) as c
    LEFT JOIN
        (
            SELECT
               *
            FROM
                %(table)s
            WHERE
                partner_id = %(partner_id)s
                {where}
            ORDER BY
                order_date DESC
            LIMIT %(limit)s
            OFFSET %(offset)s
        ) as a
    ON TRUE
    )
        """
        ).format(where=where_clause)
        params = dict(
            where_params,
            table=AsIs(self.env["alc.eshop.product.on.order"]._table),
            partner_id=self.partner.id,
            limit=per_page,
            offset=per_page * (page - 1) if (per_page and page) else None,
        )
        # pylint: disable=sql-injection
        self.env.cr.execute(
            query, params,
        )
        data = []
        res = {"size": 0, "data": data}
        size = 0
        for row in self.env.cr.dictfetchall():
            size = row["count"]
            if size == 0:
                # always return a row for the size but with no data if 0...
                break
            data.append(self._search_row_to_json(row))
        res["size"] = size
        return res

    def _search_row_to_json(self, row):
        product_family = ""
        if row["is_food"]:
            product_family = "food"
        if row["is_meds"]:
            product_family = "meds"
        if row["is_equipment"]:
            product_family = "equipment"
        return dict(
            order_line_id=row["id"],
            product_id=row["product_id"],
            description=row["description"],
            order_ref=row["order_ref"],
            order_date=utils.odoo_str_dt_to_dt_utc(row["order_date"]),
            customer_ref=(row["customer_ref"] or None),
            qty_ordered=row["qty_ordered"],
            qty_to_deliver=row["qty_to_deliver"],
            qty_in_backorder=row["qty_backorder"],
            product_family=product_family,
            is_mto=row["is_mto"],
            has_backorder=(row["qty_unavailable"] or 0) > 0,
        )

    def _get_search_where_clause(
        self,
        product_families=None,
        order_ref=None,
        order_date_min=None,
        order_date_max=None,
        customer_ref=None,
        restricts=None,
    ):

        params = {}
        wheres = [sql.SQL("")]
        family_where = []
        for product_family in product_families or []:
            if product_family == "meds":
                family_where.append(sql.SQL("is_meds"))
            elif product_family == "food":
                family_where.append(sql.SQL("is_food"))
            elif product_family == "equipment":
                family_where.append(sql.SQL("is_equipment"))
        if family_where:
            wheres.append(
                sql.SQL("(") + sql.SQL(" OR ").join(family_where) + sql.SQL(")")
            )
        if order_ref:
            wheres.append(
                sql.SQL("order_ref ilike ") + sql.Placeholder(name="order_ref")
            )
            params["order_ref"] = order_ref
        if customer_ref:
            wheres.append(
                sql.SQL("customer_ref ilike ") + sql.Placeholder(name="customer_ref")
            )
            params["customer_ref"] = customer_ref
        restrict_where = []
        for value in restricts or []:
            if value == "has_backorder":
                restrict_where.append(sql.SQL("qty_unavailable > 0"))
            elif value == "is_mto":
                restrict_where.append(sql.SQL("is_mto"))
        if restrict_where:
            wheres.append(
                sql.SQL("(") + sql.SQL(" OR ").join(restrict_where) + sql.SQL(")")
            )
        if order_date_min:
            wheres.append(
                sql.SQL("order_date >= ") + sql.Placeholder(name="order_date_min")
            )
            params["order_date_min"] = order_date_min
        if order_date_max:
            wheres.append(
                sql.SQL("order_date <= ") + sql.Placeholder(name="order_date_max")
            )
            params["order_date_max"] = order_date_max
        where_clause = sql.SQL(" AND ").join(wheres)
        return where_clause, params
