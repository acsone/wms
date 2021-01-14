# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""

Respond to calls from the ESB.

"""

from datetime import datetime

import werkzeug

import odoo
from odoo import _, http
from odoo.http import request

from odoo.addons.web.controllers.main import ensure_db


def strptime(val):
    return datetime.strptime(val, "%Y-%m-%d").date()


class StatsController(http.Controller):

    PRODUCT_TYPES = {"aliment": "ALI", "medicament": "MED", "materiel": "MAT"}

    @staticmethod
    def _validate_statistics_form(values):
        errors = []
        datefields = ("startDate", "endDate")
        for key in datefields:
            try:
                if not values.get(key):
                    continue
                strptime(values[key])
            except ValueError:
                errors.append(_("Bad date format for `%s`. Expected: YYYY-mm-dd") % key)
        if errors:
            raise werkzeug.exceptions.BadRequest("\n".join(errors))

    @http.route("/connector_esb/statistics/form", type="http", auth="user", csrf=False)
    def statistics_form(self, **kw):
        """ Return statistics for customers according to filters

        Expect a POST with application/x-www-form-urlencoded.
        Params:
        * customerErpId: partner.ref
        * startDate: format YYYY-mm-dd
        * endDate: format YYYY-mm-dd
        * productType: product family (ALI, MAT, ...)
        * manufacturer: supplier codes of the products (separated by commas)
        * language: FR / EN / NL

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env

        values = request.httprequest.form
        self._validate_statistics_form(values)

        start = values.get("startDate")
        end = values.get("endDate")
        supplier = values.get("manufacturer") or ""

        backend = env["esb.backend"].sudo().get_singleton()
        with backend.work_on("res.partner") as work:
            component = work.component("ws.message.statistics.form")
            options = component.options_for_form(
                customer_ref=values["customerErpId"],
                start=strptime(start) if start else False,
                end=strptime(end) if end else False,
                product_type=self.PRODUCT_TYPES.get(values.get("productType"), ""),
                suppliers=supplier.split(",") if supplier.strip() else False,
                language=values.get("language"),
            )
            res = component.get_message(options)
            headers = [("Content-Type", "text/xml")]
            return request.make_response(res, headers)

    @http.route(
        "/connector_esb/statistics/product/<string:sku>/" "<string:customer_ref>",
        type="http",
        auth="user",
        csrf=False,
    )
    def product_customer_stat(self, sku, customer_ref):
        """ Return a customer purchase statistics for a specific product for
            the last 12 months

        Expect a GET

        $ curl http://localhost/connector_esb/statistics/product/1322031/464

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        backend = env["esb.backend"].get_singleton()
        with backend.work_on("sale.order.line") as work:
            res = work.component("ws.message.product.customer.stat").get_message(
                customer_ref, sku
            )
            headers = [("Content-Type", "text/xml")]
            return request.make_response(res, headers)

    @http.route(
        "/connector_esb/statistics/customer/<string:customer_ref>",
        type="http",
        auth="user",
        csrf=False,
    )
    def customer_purchase_statistic(self, customer_ref):
        """ Return a customer 2 years purchase statistics by base category.

        Base categories are:
            specific_data.product_categ_ali
            specific_data.product_categ_medoc
            specific_data.product_categ_materiel
        Expect a GET : connector_esb/statistics/customer/<customer_ref>

            $ curl http://localhost:8069/connector_esb/statistics/customer/469

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        backend = env["esb.backend"].get_singleton()
        with backend.work_on("sale.order.line") as work:
            res = work.component("ws.message.customer.stat").get_message(customer_ref)
            headers = [("Content-Type", "text/xml")]
            return request.make_response(res, headers)

    @http.route(
        "/connector_esb/totalorder/customer/<string:customer_ref>",
        type="http",
        auth="public",
        csrf=False,
    )
    def customer_delivery_fee(self, customer_ref):
        """ Return info to calculate a customer delivery fee

        Expect a GET

        $ curl http://localhost:8069/connector_esb/totalorder/customer/464

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        backend = env["esb.backend"].get_singleton()

        with backend.work_on("res.partner") as work:
            res = work.component("ws.message.customer.delivery.fee").get_message(
                customer_ref
            )
            headers = [("Content-Type", "text/xml")]
            return request.make_response(res, headers)
