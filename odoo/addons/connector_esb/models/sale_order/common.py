# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
from datetime import datetime

from psycopg2 import IntegrityError

from odoo import _, api, exceptions, fields, models
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "esb.exportable"]

    esb_ref = fields.Char(string="Reference for ESB", copy=False)

    _sql_constraints = [
        ("esb_ref_unique", "unique(esb_ref)", _("This reference esb already exists"))
    ]

    @api.multi
    def esb_is_exportable(self):
        exportable = super(SaleOrder, self).esb_is_exportable() and self.state not in (
            "draft",
            "sent",
            "confirm_background",
        )
        return exportable

    @api.model
    def create(self, vals):
        self_ctx = self.with_context(_sale_order_create=True)
        return super(SaleOrder, self_ctx).create(vals)

    @api.multi
    def write(self, vals):
        self_ctx = self.with_context(_sale_order_write=True)
        return super(SaleOrder, self_ctx).write(vals)

    @job(default_channel="root.background.esb")  # priority=2
    def ws_create_new(self, data, creation_date=None):
        """Create a sale order with data coming from webservices

        The creation_date is the date of when the controller called to create
        the sale in datetime's format. It is required because in some cases, we
        cancel the SO after some delay between the creation of the job and its
        execution (see module sale_delay).
        """
        # This is kept only for backward compatibility so that jobs previously
        # created without the argument do not fail to execute. All new jobs
        # will pass the parameter so some time after the deployment, we can
        # remove the next 2 lines and make 'creation_date' a positional
        # argument.
        if creation_date is None:
            creation_date = datetime.now()
        try:
            return self.with_context(no_connector_export=True)._ws_create_new(
                data, creation_date
            )
        except IntegrityError as error:
            self.env.cr.rollback()
            _logger.error("Webservice create saleorder, integrity error : %s", error)
            raise

    def _ws_create_new(self, data, creation_date):
        order_data = self._ws_create_order_data(data)
        order_data = self.env["sale.order"].play_onchanges(
            order_data,
            [
                "discount_pricelist_id",
                "supplier_promotion_allowed",
                "partner_id",
                "team_id",
            ],
        )
        # never send notify mail on creation from jobs
        order = self.with_context(mail_auto_subscribe_no_notify=True).create(order_data)

        partner_ref = data["customer_id"]

        is_sale_in_exception = False
        for line in self._ws_create_order_line_data(data)[:]:
            if line["product_id"] == "":
                # Unknown product just log the error in the chatter
                order.message_post(
                    body="Product with {} : {} was not found".format(
                        line["code_type"], line["code_searched"]
                    )
                )
                continue
            line["order_id"] = order.id
            changed_line = self.env["sale.order.line"].play_onchanges(
                line, ["product_id"]
            )
            line_rec = self.env["sale.order.line"].create(changed_line)

            # Check if the line contains an exception.
            # In this case, change the qty to 0
            if line_rec.exception:
                is_sale_in_exception = True
                # FIXME: add boolean on res_partner to filter web service users
                if partner_ref in ("8114", "8264"):
                    # NewPharma
                    line_rec.write({"product_uom_qty": 0, "ignore_exception": True})
                else:
                    line_rec.write({"ignore_exception": True})

        # If there is at least one line in exception, we need to set
        # the flag "ignore_exception" to True on the sale.order.
        # Otherwise the method detect_exceptions will return True
        if is_sale_in_exception:
            order.ignore_exception = True
        if order.is_delayed(creation_date):
            order.action_cancel()
            order.message_post(
                body=_(
                    "Was automatically cancelled on creation because the"
                    "job took longer to execute than the customer allows."
                )
            )
        else:
            order.action_confirm_background()
        return order

    def _ws_get_partner(self, ref):
        partner = self.env["res.partner"].search(
            [("ref", "=", ref)],
            # For main partner and contacts having the same ref, the sort
            # order forces for the main contact to be returned.
            # Which is the one with parent_id set at Null.
            order="parent_id desc",
            limit=1,
        )
        if not partner:
            raise exceptions.MissingError(_("No match found for customer_id: %s") % ref)
        return partner

    @staticmethod
    def _ws_get_date_order(ws_date):
        """Return the creation date of an order from WS"""
        if " " in ws_date:
            # we have a complete datetime, use it
            return ws_date
        else:
            # We have only the date, if the order is for today,
            # we use the current time (time of import). If the order
            # is from a previous day, we hard-code the time at the middle
            # of the day arbitrarily.
            # With this solution, it means that an order created on Magento
            # at days N-1 23:59 and imported at day N will have an order_date
            # of N-1 12:00. This is maybe the best we can do if we are not
            # provided a time anyway.
            now_date, _spc, now_time = fields.Datetime.now().partition(" ")
            if ws_date == now_date:
                return ws_date + " " + now_time
            else:
                return ws_date + " 12:00:00"

    def _ws_create_order_data(self, data):
        order_data = {}
        partner_ref = data["customer_id"]
        partner = self._ws_get_partner(partner_ref)
        order_data["team_id"] = self.env.ref("sales_team.salesteam_website_sales").id
        order_data["esb_ref"] = data["increment_id"]
        order_data["partner_id"] = partner.id
        order_data["date_order"] = self._ws_get_date_order(data["date"])
        order_data["client_order_ref"] = data["order_ref"]
        order_data["state"] = "draft"
        if "num_suite" in data:
            order_data["suite_name"] = data["num_suite"]
        if data.get("carrier_id"):
            carrier = (
                self.env["delivery.carrier"]
                .search([("esb_ref", "=", data["carrier_id"])])
                .exists()
            )
            if len(carrier) == 1:
                order_data["carrier_id"] = carrier.id
            elif len(carrier) > 1:
                _logger.error(
                    "Webservice new saleorder, multiple carrier found for %s.",
                    data["carrier_id"],
                )
            else:
                _logger.error(
                    "Webservice new saleorder, carrier %s not found", data["carrier_id"]
                )
        elif partner.property_delivery_carrier_id:
            order_data["carrier_id"] = partner.property_delivery_carrier_id.id
        return order_data

    def _ws_create_order_line_data(self, data):
        lines = []
        human_categ = self.env.ref("specific_data.product_categ_humain")
        for line in data["lines"]:
            if "sku" in line:
                is_sku = True
                product = self.env["product.product"].search(
                    [("default_code", "=", line["sku"])]
                )
            elif "cnk" in line:
                is_sku = False
                product = self.env["product.product"].search(
                    [("cnk_code", "=", line["cnk"])]
                )
            else:
                message = "You need to provide the SKU or the CNK"
                _logger.error(message)
                raise exceptions.UserError(_(message))

            if line.get("free"):
                # free line
                # check if product is human
                # if additional product (not human med), skip it
                if not product or product.categ_id != human_categ:
                    continue

            product_code = is_sku and line["sku"] or line["cnk"]
            if len(product) > 1:
                message = (
                    "Webservice new saleorder, several"
                    " products with the same sku/cnk %s found"
                )
                _logger.error(message, product_code)
                raise exceptions.UserError(_(message) % product_code)

            sol = {}
            if len(product):
                sol["product_id"] = product.id
                sol["name"] = product.name
                sol["product_uom"] = product.uom_id.id
                sol["product_uom_qty"] = line.pop("quantity")
                sol["discounting_type"] = "multiplicative"
                sol["esb_ref"] = line.pop("line_id")
            else:
                # Product not found
                sol["product_id"] = ""
                sol["code_type"] = "SKU" if is_sku else "CNK"
                sol["code_searched"] = product_code
            lines.append(sol)

        return lines
