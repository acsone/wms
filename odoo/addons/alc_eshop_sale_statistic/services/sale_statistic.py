# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
from collections import OrderedDict

from dateutil.relativedelta import relativedelta

from odoo import _, fields
from odoo.exceptions import MissingError
from odoo.tools import float_round

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class SaleStatsService(Component):
    """Provides statistics on sales related to the customer."""

    _inherit = "base.rest.service"
    _name = "sale.statistic.service"
    _collection = "shopinvader.backend"
    _usage = "sale_statistics"

    @restapi.method(
        [(["/monthly_purchased/<int:product_id>"], "GET")],
        output_param=restapi.CerberusValidator("_monthly_sales_output_schema"),
    )
    def monthly_purchased(self, product_id):
        """Returns the monthly quantity purchased during the last 12 months for
        the given product. (The current month is excluded)"""
        product = self.env["product.product"].browse(product_id).exists()
        if not product:
            raise MissingError(_("Product not found for id %s") % product_id)
        return self._get_monthly_purchased(product)

    ############
    # validators
    ############
    def _monthly_sales_output_schema(self):
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

    def _get_monthly_purchased(self, product):
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
