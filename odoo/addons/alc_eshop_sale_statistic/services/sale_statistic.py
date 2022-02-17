# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime
from collections import OrderedDict

from dateutil.relativedelta import relativedelta
from psycopg2.extensions import AsIs

from odoo import _, fields
from odoo.exceptions import MissingError
from odoo.tools import float_round

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class SaleStatsService(Component):
    """Provides statistics on sales related to the customer."""

    _inherit = "base.rest.service"
    _name = "sale.statistic.service"
    _collection = "shopinvader.backend"
    _usage = "sale_statistics"

    @restapi.method(
        [(["/monthly_ordered/<int:product_id>"], "GET")],
        output_param=restapi.CerberusValidator("_monthly_ordered_output_schema"),
    )
    def monthly_ordered(self, product_id):
        """Returns the monthly quantity ordered during the last 12 months for
        the given product.

        (The current month is excluded)
        """
        product = self.env["product.product"].browse(product_id).exists()
        if not product:
            raise MissingError(_("Product not found for id %s") % product_id)
        return self._get_monthly_ordered(product)

    @restapi.method(
        [(["/top_ordered"], "GET")],
        input_param=restapi.CerberusValidator("_top_ordered_input_schema"),
        output_param=restapi.CerberusValidator("_top_ordered_output_schema"),
    )
    def top_ordered(
        self,
        page=None,
        per_page=None,
        product_family=None,
        supplier_discount_only=False,
    ):
        """Search the most ordered product along the last 12 months."""
        return self._get_top_ordered(
            page=page,
            per_page=per_page,
            product_family=product_family,
            supplier_discount_only=supplier_discount_only,
        )

    ############
    # validators
    ############
    def _monthly_ordered_output_schema(self):
        """
        Output validator for the search
        :return: dict
        """
        return {
            "average": {"type": "float", "required": True, "nullable": False},
            "months": {
                "meta": {
                    "description": "A month / average qty mapping ordered "
                    "bu month (older first) ",
                    "example": {"2021-01-02": 5.0},
                },
                "type": "dict",
                "required": True,
                "nullable": True,
                "keysrules": {"type": "string"},
                "valuesrules": {"type": "float", "required": True, "nullable": False},
            },
        }

    def _top_ordered_input_schema(self):
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
            "product_family": {
                "type": "string",
                "allowed": ["all", "meds", "food", "equipment"],
                "default": "all",
                "nullable": False,
            },
            "supplier_discount_only": {
                "type": "boolean",
                "default": False,
                "nullable": False,
            },
        }

    def _top_ordered_output_schema(self):
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "product_id": {
                            "coerce": to_int,
                            "nullable": False,
                            "required": True,
                            "type": "integer",
                        },
                        "ordered_count": {
                            "coerce": to_int,
                            "nullable": False,
                            "required": True,
                            "type": "integer",
                        },
                        "product_family": {
                            "type": "string",
                            "allowed": ["meds", "food", "equipment"],
                            "nullable": False,
                        },
                        "date_last_ordered": {
                            "type": "string",
                            "required": True,
                            "nullable": False,
                        },
                    },
                },
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

    def _get_monthly_ordered(self, product):
        today = datetime.date.today()
        periods = OrderedDict()
        date_start = datetime.date(today.year - 1, today.month, 1)
        date_end = datetime.date(today.year, today.month, 1)
        sql = """
            SELECT
                SUM(product_uom_qty - COALESCE(product_qty_canceled, 0) ),
                CAST(date_trunc('month', date_order) AS date)
            FROM
                sale_order_line sol
                join sale_order so on so.id =  sol.order_Id
            WHERE
                product_id=%(product_id)s
                AND partner_id=%(partner_id)s
                AND order_partner_id=%(partner_id)s
                AND date_order >= %(date_start)s
                AND date_order < %(date_end)s
                AND so.sale_channel IN ('web', 'mail', 'phone', 'fax')
                AND so.state in ('done', 'sale')
            GROUP BY
                CAST(date_trunc('month', date_order) AS date);
        """
        self.env.cr.execute(
            sql,
            dict(
                product_id=product.id,
                partner_id=self.partner.id,
                date_start=date_start,
                date_end=date_end,
            ),
        )
        result = self.env.cr.fetchall()
        total = 0
        rounding = product.uom_id.rounding
        _date = date_start
        for _m in range(12):
            periods.setdefault(fields.Date.to_string(_date), 0)
            _date += relativedelta(months=1)
        for qty, date in result:
            periods[date] = float_round(qty, precision_rounding=rounding)
            total += qty
        monthly_average = total / 12.0
        monthly_average = float_round(monthly_average, precision_rounding=rounding)
        return {
            "average": monthly_average,
            "months": periods,
        }

    def _get_top_ordered(
        self,
        page=None,
        per_page=None,
        product_family=None,
        supplier_discount_only=False,
    ):
        sql = """
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
                %(where)s
        ) as c
    LEFT JOIN
        (
            SELECT
               *
            FROM
                %(table)s
            WHERE
                partner_id = %(partner_id)s
                %(where)s
            ORDER BY
                ordered_count DESC
            LIMIT %(limit)s
            OFFSET %(offset)s
        ) as a
    ON TRUE
    )
        """
        wheres = ["\n"]
        if product_family == "meds":
            wheres.append("AND is_meds")
        elif product_family == "food":
            wheres.append("AND is_food")
        elif product_family == "equipment":
            wheres.append("AND is_equipment")
        if supplier_discount_only:
            wheres.append("AND in_supplier_promotion")
        self.env.cr.execute(
            sql,
            {
                "table": AsIs(self.env["alc.eshop.product.ordered.qty"]._table),
                "partner_id": self.partner.id,
                "where": AsIs("\n".join(wheres)),
                "limit": per_page,
                "offset": per_page * (page - 1) if (per_page and page) else None,
            },
        )
        data = []
        res = {"size": 0, "data": data}
        size = 0
        for row in self.env.cr.dictfetchall():
            size = row["count"]
            if size == 0:
                # always return a row for the size but with no data if 0...
                break
            product_family = ""
            if row["is_food"]:
                product_family = "food"
            if row["is_meds"]:
                product_family = "meds"
            if row["is_equipment"]:
                product_family = "equipment"
            data.append(
                {
                    "product_id": row["product_id"],
                    "ordered_count": row["ordered_count"],
                    "date_last_ordered": self._dt_to_isoformat(
                        row["date_last_ordered"]
                    ),
                    "product_family": product_family,
                }
            )
        res["size"] = size
        return res

    def _dt_to_isoformat(self, date_str):
        value = fields.Datetime.from_string(date_str)
        # Get the timestamp converted to the client's timezone.
        # This call also add the tzinfo into the datetime object
        value = fields.Datetime.context_timestamp(self.partner, value)
        return value.isoformat()
