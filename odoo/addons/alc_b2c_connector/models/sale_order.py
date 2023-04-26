# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import dateutil
import pytz

from odoo import Command, _, api, fields
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.osv.expression import AND
from odoo.tests.common import Form

from odoo.addons.sale.models.sale_order import SaleOrder as SaleOrderBase

from .res_partner import TITLE_XML_ID_BY_B2C_KEY


class SaleOrder(SaleOrderBase):

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
    def _create_from_b2c(self, data, endpoint_setting):
        """Create a sale order with data coming from b2c."""
        body = _("Order created from json: {data}.").format(data=data)
        order_data = self._parse_b2c_order(data, endpoint_setting)
        order = (
            self.env["sale.order"]
            .with_context(mail_auto_subscribe_no_notify=True)
            .create(order_data)
        )
        order.message_post(body=body)
        order.action_confirm()
        return order

    def _cancel_from_b2c(self):
        """Cancel a sale order with data coming from b2c."""

        self.ensure_one()
        if self.picking_ids and any(self.mapped("picking_ids.printed")):
            body = _("Cannot cancel order {name} , being process already").format(
                name=self.name
            )
        else:
            body = _("Order  {name} cancelled from b2c api.").format(name=self.name)
            self.with_context(disable_cancel_warning=True).action_cancel()

        self.message_post(body=body)
        return self

    def _update_from_b2c(self, data, endpoint_setting):
        """Update a sale order with data coming from b2c.

        This is possible as long as the order
        is not confirmed
        """
        self.ensure_one()
        if "done" in self.mapped("picking_ids.state"):
            raise ValidationError(
                _("You cannot update a sale order that is already ready for delivery")
            )
        if "lines" not in data and "recipient" not in data:
            raise ValidationError(_("Missing update parameters, lines or recipient."))
        self.with_context(disable_cancel_warning=True).action_cancel()
        self.action_draft()
        if "lines" in data:
            self._update_lines_from_b2c(data, endpoint_setting)
        if "recipient" in data:
            partner = self._get_final_b2c_recipient(data, endpoint_setting)
            self._update_recipient_from_b2c(partner)
        self.action_confirm()
        return self

    def _update_lines_from_b2c(self, data, endpoint_setting):
        self.order_line.unlink()
        sale_order_form = Form(self)
        line_vals_list = []
        for line_info in self._parse_b2c_order_line(data, endpoint_setting):
            with sale_order_form.order_line.new() as line_form:
                line_form.product_id = line_info["product_id"]
                line_form.name = line_info["name"]
                line_form.product_uom_qty = line_info["product_uom_qty"]
            line_vals = line_form._values_to_save()
            line_vals["b2c_ref"] = line_info["b2c_ref"]
            line_vals_list.append(line_vals)
        self.write(
            {"order_line": [Command.create(line_vals) for line_vals in line_vals_list]}
        )
        body = _("Sale Order  {sale_order} updated from json: {json_file}.").format(
            sale_order=self.name,
            json_file=data,
        )
        self.message_post(body=body)

    def _update_recipient_from_b2c(self, partner):
        if self.partner_id != partner:
            self.partner_id = partner

    @api.model
    def _parse_b2c_order(self, data, endpoint_setting):
        sale_order_form = Form(
            self.with_context(
                default_date_order=data["date"],
                default_pricelist_id=endpoint_setting.pricelist_id.id,
            )
        )
        # we create all the orders with the VET as final customer
        # At the end of the process and after the onchange call, the partner_id
        # will be replaced by the final customer
        partner_vet = self.env["res.partner"]._get_partner_by_ref(data["customer_ref"])
        # get the parther and play onchange to get shipping,
        sale_order_form.partner_id = partner_vet
        sale_order_form.sale_channel_id = endpoint_setting.sale_channel_id
        sale_order_form.team_id = endpoint_setting.sale_team_id
        if endpoint_setting.payment_mode_id:
            sale_order_form.payment_mode_id = endpoint_setting.payment_mode_id
        # replace partner by the final customer
        sale_order_form.partner_id = self._get_final_b2c_recipient(
            data, endpoint_setting
        )
        # ensure specific values from the backend are preserved
        sale_order_form.payment_term_id = endpoint_setting.payment_term_id
        sale_order_form.picking_policy = endpoint_setting.picking_policy
        line_vals_list = []
        for line_info in self._parse_b2c_order_line(data, endpoint_setting):
            with sale_order_form.order_line.new() as line_form:
                line_form.product_id = line_info["product_id"]
                line_form.name = line_info["name"]
                line_form.product_uom_qty = line_info["product_uom_qty"]
            line_vals = line_form._values_to_save()
            line_vals["b2c_ref"] = line_info["b2c_ref"]
            line_vals_list.append(line_vals)
        values = sale_order_form._values_to_save()
        values["b2c_ref"] = data["id"]
        values["order_line"] = [
            Command.create(line_vals) for line_vals in line_vals_list
        ]
        return values

    @api.model
    def _parse_b2c_order_line(self, data, endpoint_setting):
        lines_data = [line._convert_to_write() for line in data["lines"]]
        skus = [line["sku"] for line in lines_data]
        domain = [("default_code", "in", skus)]
        if endpoint_setting.product_assortment_id:
            product_assortment_domain = (
                endpoint_setting.product_assortment_id._get_eval_domain()
            )
            domain = AND([product_assortment_domain, domain])
        products = self.env["product.product"].search(domain)
        product_by_sku = {p.default_code: p for p in products}
        unknown_skus = set(skus).difference(set(product_by_sku.keys()))
        if unknown_skus:
            raise ValidationError(_("Unknowns SKU(s): %s " ", ".join(unknown_skus)))
        result = []
        for line_data in lines_data:
            sol = {}
            product = product_by_sku[line_data["sku"]]
            sol["product_id"] = product
            sol["name"] = product.name
            sol["product_uom_qty"] = line_data.pop("quantity")
            sol["b2c_ref"] = line_data.pop("line_id")
            result.append(sol)
        return result

    @api.model
    def _get_final_b2c_recipient(self, data, endpoint_setting):
        customer_info = data["recipient"]._convert_to_write()
        b2c_ref = self.env["res.partner"]._b2c_id_to_b2c_ref(
            customer_info["id"], endpoint_setting
        )
        partner = self.env["res.partner"]._get_partner_by_ref(
            b2c_ref, raise_if_notfound=False
        )
        if partner:
            partner._update_b2c_data(customer_info, endpoint_setting)
            return partner
        name = customer_info["first_name"]
        last_name = customer_info.get("last_name")
        if last_name:
            name = f"{name} {last_name}"
        title = customer_info.get("title").value
        if title:
            title = self.env.ref(TITLE_XML_ID_BY_B2C_KEY[title]).id
        country_id = None
        country_code = customer_info.get("country_code").value
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
                # FIXME: where this field is gone
                # "is_sale_back_order_accepted": endpoint_setting.is_sale_back_order_accepted,
                "is_b2c_customer": True,
                "partner_type": "student_like",
                "ref": b2c_ref,
                "country_id": country_id,
                # FIXME: do after specific_partner migration
                # "suite": customer_info.get("name2"),
                "comment": customer_info.get("note"),
            }
        )

    @api.model
    def _parse_datetime_to_utc(self, dt):
        """Parse an iso8601-formatted date string and returns.

        a DT into UTC without TZ info as string
        """
        dt = dateutil.parser.parse(dt)
        dt = dt.astimezone(pytz.timezone("UTC"))
        return fields.Datetime.to_string(dt)

    @api.constrains("sale_channel")
    def _check_sale_channel_selection(self):
        user = self.env.user
        b2c_xmlid = "alc_b2c_connector.alc_b2c_rest_api_user"
        if not user._is_superuser() and user != self.env.ref(b2c_xmlid):
            b2c_channels = self._get_sale_channels_external()
            if any(c in b2c_channels for c in self.mapped("sale_channel")):
                msg = _("You cannot use this sale channel for manuel order")
                raise ValidationError(msg)

    @api.model
    def _get_base_search_domain(self, endpoint_setting):
        return [("sale_channel_id", "=", endpoint_setting.sale_channel_id.id)]

    def _get_order_from_b2c_ref(self, b2c_ref, endpoint_setting, extended_domain=None):
        domain = self._get_base_search_domain(endpoint_setting)
        domain = expression.AND([domain, [("b2c_ref", "=", b2c_ref)]])
        if extended_domain:
            domain = expression.AND([domain, extended_domain])
        res = self.search(domain)
        if not res:
            raise ValidationError(
                _("Sale order not found for id {b2c_ref}").format(b2c_ref=b2c_ref)
            )
        return res

    def _search_orders_from_b2c(
        self, b2c_refs: list, limit: int, offset: int, endpoint_setting
    ):
        domain = self._get_base_search_domain(endpoint_setting)
        if b2c_refs:
            domain = expression.AND([domain, [("b2c_ref", "in", b2c_refs)]])
        return self.search(domain, limit=limit, offset=offset)
