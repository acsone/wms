# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

import dateutil
import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND

from .res_partner import TITLE_XML_ID_BY_B2C_KEY


class SaleOrder(models.Model):

    _inherit = "sale.order"

    b2c_ref = fields.Char(string="Reference B2C", copy=False, index=True)
    b2c_state = fields.Selection(
        string="B2C state",
        selection=[
            ("draft", "Draft"),
            ("sale", "Sale"),
            ("cancel", "Cancel"),
            ("delivery", "Delivery"),
        ],
        compute="_compute_b2c_state",
    )

    _sql_constraints = [
        (
            "b2c_ref_unique",
            "EXCLUDE (b2c_ref WITH =, sale_channel WITH =) WHERE (b2c_ref <> '' or b2c_ref is not null)",
            _("This b2c reference already exists"),
        )
    ]

    @api.depends(
        "state",
        "order_line",
        "order_line.product_qty_remains_to_deliver",
        "order_line.qty_delivered",
    )
    @api.multi
    def _compute_b2c_state(self):
        for record in self:
            state = "draft"
            if record.state == "cancel":
                state = "cancel"
            elif record.state in ("sale", "done"):
                if any(record.mapped("order_line.qty_delivered")):
                    state = "delivery"
                else:
                    state = "sale"
            record.b2c_state = state

    @api.model
    def _create_from_b2c(self, data, b2c_backend):
        """ Create a sale order with data coming from b2c
        """
        body = _("Order created from json: %s.") % json.dumps(data, sort_keys=True)
        order_data = self._parse_b2c_order(data, b2c_backend)
        order = (
            self.env["sale.order"]
            .with_context(mail_auto_subscribe_no_notify=True)
            .create(order_data)
        )
        order.message_post(body=body)
        order.sudo().action_confirm_background()
        return order

    @api.model
    def _cancel_from_b2c(self):
        """ Cancel a sale order with data coming from b2c
        """

        self.ensure_one()
        if self.picking_ids and any(self.mapped("picking_ids.printed")):
            body = _("Cannot cancel order %s , being process already") % self.name
        else:
            body = _("Order  %s cancelled from b2c api.") % self.name
            self.action_cancel()

        self.message_post(body=body)
        return self

    @api.model
    def _parse_b2c_order(self, data, b2c_backend):
        order_data = {}
        # we create all the orders with the VET as final customer
        # At the end of the process and after the onchange call, the partner_id
        # will be replaced by the final customer
        partner_vet = self.env["res.partner"]._get_partner_by_ref(data["customer_ref"])
        # get the parther and play onchange to get shipping,
        order_data["partner_id"] = partner_vet.id
        order_data["b2c_ref"] = data["id"]
        order_data["sale_channel"] = b2c_backend.sale_channel
        order_data["date_order"] = self._parse_datetime_to_utc(data["date"])
        order_data["team_id"] = b2c_backend.sale_team_id.id
        if b2c_backend.payment_mode_id:
            order_data["payment_mode_id"] = b2c_backend.payment_mode_id.id
        # invvoice, payment_term, pricelist, carrier_id, team
        updated_data = self.play_onchanges(order_data, order_data.keys())
        order_data.update(updated_data)

        # replace partner by the final customer
        order_data["partner_id"] = self._get_final_b2c_recipient(data, b2c_backend).id
        # ensure specific values from the backend are preserved
        order_data["pricelist_id"] = b2c_backend.pricelist_id.id
        order_data["payment_term_id"] = b2c_backend.payment_term_id.id
        order_data["picking_policy"] = b2c_backend.picking_policy
        order_data["order_line"] = [
            (0, 0, line_info)
            for line_info in self._parse_b2c_order_line(data, b2c_backend)
        ]
        return order_data

    @api.model
    def _parse_b2c_order_line(self, data, b2c_backend):
        lines_data = data["lines"]
        skus = [line["sku"] for line in lines_data]
        domain = b2c_backend.product_assortment_id._get_eval_domain()
        domain = AND([domain, [("default_code", "in", skus)]])
        products = self.env["product.product"].search(domain)
        product_by_sku = {p.default_code: p for p in products}
        unknown_skus = set(skus).difference(set(product_by_sku.keys()))
        if unknown_skus:
            raise ValidationError(_("Unknowns SKU(s): %s " ", ".join(unknown_skus)))
        result = []
        for line_data in lines_data:
            sol = {}
            product = product_by_sku[line_data["sku"]]
            sol["product_id"] = product.id
            sol["name"] = product.name
            sol["product_uom"] = product.uom_id.id
            sol["product_uom_qty"] = line_data.pop("quantity")
            sol["b2c_ref"] = line_data.pop("line_id")
            sol["discounting_type"] = "multiplicative"
            result.append(sol)
        return result

    @api.model
    def _get_final_b2c_recipient(self, data, b2c_backend):
        customer_info = data["recipient"]
        b2c_ref = self.env["res.partner"]._b2c_id_to_b2c_ref(
            customer_info["id"], b2c_backend
        )
        partner = self.env["res.partner"]._get_partner_by_ref(
            b2c_ref, raise_if_notfound=False
        )
        if partner:
            # DO WE HAVE TO UPDATE ADDRESS INFO?
            return partner
        name = customer_info["first_name"]
        last_name = customer_info.get("last_name")
        if last_name:
            name = u"{} {}".format(name, last_name)
        title = customer_info.get("title")
        if title:
            title = self.env.ref(TITLE_XML_ID_BY_B2C_KEY[title]).id
        country_id = None
        country_code = customer_info.get("country_code")
        if country_code:
            country_id = self.env["res.country"]._get_by_code(country_code).id
        return self.env["res.partner"].create(
            {
                "name": name,
                "title": title,
                "email": customer_info.get("email"),
                "street": customer_info.get("street"),
                "street2": customer_info.get("street2"),
                "zip": customer_info.get("zip"),
                "city": customer_info.get("city"),
                "phone": customer_info.get("phone"),
                "mobile": customer_info.get("mobile"),
                "is_sale_back_order_accepted": b2c_backend.is_sale_back_order_accepted,
                "is_b2c_customer": True,
                "alcyon_category_id": self.env.ref(
                    "specific_partner.partner_category_student"
                ).id,
                "ref": b2c_ref,
                "country_id": country_id,
            }
        )

    @api.model
    def _parse_datetime_to_utc(self, dt):
        """Parse an iso8601-formatted date string and returns
        a DT into UTC without TZ info as string
        """
        dt = dateutil.parser.parse(dt)
        dt = dt.astimezone(pytz.timezone("UTC"))
        return fields.Datetime.to_string(dt)

    @api.constrains("sale_channel")
    def _check_sale_channel_selection(self):
        if (
            self.sale_channel == "chronovet" or self.sale_channel == "placedesvetos"
        ) and (
            self.env.user != self.env.ref("alc_b2c_connector.alc_b2c_rest_api_user")
            and self.env.user != self.env.ref("base.user_root")
        ):
            raise ValidationError(
                _("You cannot use this sale channel for manuel order")
            )
