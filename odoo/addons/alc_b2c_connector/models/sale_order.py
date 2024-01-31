# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

import dateutil
import pytz

from odoo import Command, _, api, fields
from odoo.exceptions import MissingError, ValidationError
from odoo.osv import expression
from odoo.osv.expression import AND

from odoo.addons.sale.models.sale_order import SaleOrder as SaleOrderBase

from .alc_b2c_client import AlcB2cClient
from .res_partner import ResPartner

_logger = logging.getLogger(__name__)


class SaleOrder(SaleOrderBase):
    alc_b2c_client_id = fields.Many2one[AlcB2cClient](readonly=True)
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
    message_partner_ids = fields.Many2many[ResPartner](
        compute_sudo=True
    )  # This field required
    # base.group_user access, make it compute_sudo to avoid access right issue for b2c
    # user
    _sql_constraints = [
        (
            "b2c_ref_unique",
            "EXCLUDE (b2c_ref WITH =, sale_channel_id WITH =) WHERE (b2c_ref <> '' or b2c_ref is not null)",
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
    def _create_from_b2c(self, data, b2c_client):
        """Create a sale order with data coming from b2c."""
        body = _("Order created from json: {data}.").format(data=data)
        order_data = self._parse_b2c_order(data, b2c_client)
        order = (
            self.env["sale.order"]
            .with_context(
                mail_auto_subscribe_no_notify=True,
                tracking_disable=True,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
            )
            .create(order_data)
        )
        order.message_post(body=body)
        # the vet is set to as the shipping_address, so the procurement group is created
        # for him, as the b2c user don't have access to the vet, it needs sudo to perform
        order.sudo().action_confirm()
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
            self.with_context(disable_cancel_warning=True).sudo().action_cancel()

        self.message_post(body=body)
        return self

    def _update_from_b2c(self, data, b2c_client):
        """Update a sale order with data coming from b2c.

        This is possible as long as the order
        is not confirmed
        """
        self.ensure_one()
        if "done" in self.mapped("picking_ids.state"):
            msg = _("You cannot update a sale order that is already ready for delivery")
            _logger.error(msg)
            raise ValidationError(msg)
        if "lines" not in data and "recipient" not in data:
            msg = _("Missing update parameters, lines or recipient.")
            _logger.error(msg)
            raise ValidationError(msg)
        self.sudo().with_context(disable_cancel_warning=True).action_cancel()
        self.action_draft()
        if "lines" in data:
            self._update_lines_from_b2c(data, b2c_client)
        if "recipient" in data:
            partner = self._get_final_b2c_recipient(data, b2c_client)
            self._update_recipient_from_b2c(partner)
        # the vet is set to as the shipping_address, so the procurement group is created
        # for him, as the b2c user don't have access to the vet, it needs sudo to perform
        # action_confirm
        self.sudo().action_confirm()
        return self

    def _update_lines_from_b2c(self, data, b2c_backend):
        order = self.with_context(
            mail_auto_subscribe_no_notify=True,
            tracking_disable=True,
            mail_create_nolog=True,
            mail_create_nosubscribe=True,
            mail_notrack=True,
        )
        order.order_line.unlink()
        data_lines = self._parse_b2c_order_line(data, b2c_backend)
        order.write({"order_line": [(0, 0, line) for line in data_lines]})
        body = _("Sale Order  {sale_order} updated from json: {json_file}.").format(
            sale_order=self.name,
            json_file=data,
        )
        order.message_post(body=body)

    def _prepare_update_recipient_from_b2c_vals(self, partner):
        return {"partner_id": partner.id}

    def _update_recipient_from_b2c(self, partner):
        if self.partner_id != partner:
            vals = self._prepare_update_recipient_from_b2c_vals(partner)
            self.sudo().write(vals)

    @api.model
    def _parse_b2c_order(self, data, b2c_client):
        order_data = {}
        # we create all the orders with the VET as final customer
        # At the end of the process and after the onchange call, the partner_id
        # will be replaced by the final customer
        # b2c user don't have access to vet partners, we use sudo to get the partner id
        partner_vet = (
            self.env["res.partner"].sudo()._get_partner_by_ref(data["customer_ref"])
        )
        # get the parther and play onchange to get shipping,
        order_data["partner_id"] = partner_vet.id
        order_data["b2c_ref"] = data["id"]
        order_data["sale_channel_id"] = b2c_client.sale_channel_id.id
        order_data["date_order"] = self._convert_datetime_to_utc(data["date"])
        order_data["team_id"] = b2c_client.sale_team_id.id
        if b2c_client.payment_mode_id:
            order_data["payment_mode_id"] = b2c_client.payment_mode_id.id
        # play onchange with sudo as the b2c user don't have access to the vet partner
        updated_data = self.sudo().play_onchanges(order_data, order_data.keys())
        order_data.update(updated_data)

        # replace partner by the final customer
        order_data["partner_id"] = self._get_final_b2c_recipient(data, b2c_client).id
        # ensure specific values from the backend are preserved
        order_data["pricelist_id"] = b2c_client.pricelist_id.id
        order_data["payment_term_id"] = b2c_client.payment_term_id.id
        order_data["picking_policy"] = b2c_client.picking_policy
        order_data["order_line"] = [
            Command.create(line_info)
            for line_info in self._parse_b2c_order_line(data, b2c_client)
        ]
        order_data["alc_b2c_client_id"] = b2c_client.id
        return order_data

    @api.model
    def _parse_b2c_order_line(self, data, b2c_client):
        lines_data = data["lines"]
        skus = [line["sku"] for line in lines_data]
        domain = b2c_client.product_assortment_id._get_eval_domain()
        domain = AND([domain, [("default_code", "in", skus)]])
        products = self.env["product.product"].search(domain)
        product_by_sku = {p.default_code: p for p in products}
        unknown_skus = set(skus).difference(set(product_by_sku.keys()))
        if unknown_skus:
            msg = _("Unknowns SKU(s): %s " ", ".join(unknown_skus))
            _logger.error(msg)
            raise ValidationError(msg)
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
    def _get_final_b2c_recipient(self, data, b2c_client):
        customer_info = data["recipient"]
        b2c_ref = self.env["res.partner"]._b2c_id_to_b2c_ref(
            customer_info["id"], b2c_client
        )
        partner = self.env["res.partner"]._get_partner_by_ref(
            b2c_ref, raise_if_notfound=False
        )
        if partner:
            partner._update_b2c_data(customer_info, b2c_client)
            return partner
        return self.env["res.partner"]._create_b2c_partner(customer_info, b2c_client)

    @api.model
    def _convert_datetime_to_utc(self, dt):
        """Parse an iso8601-formatted date string and returns.

        a DT into UTC without TZ info as string
        """
        if isinstance(dt, str):
            dt = dateutil.parser.parse(dt)
        return dt.astimezone(pytz.timezone("UTC")).replace(tzinfo=None)

    @api.constrains("sale_channel_id", "b2c_ref")
    def _check_sale_channel_selection(self):
        user = self.env.user
        msg = _("You cannot use this sale channel for manuel order")
        for rec in self:
            if (
                not user._is_superuser()
                and not self.env.su
                and not rec.b2c_ref
                and not rec.sale_channel_id.is_internal
            ):
                _logger.error(msg)
                raise ValidationError(msg)

    @api.model
    def _get_base_search_domain(self, b2c_client):
        return [("sale_channel_id", "=", b2c_client.sale_channel_id.id)]

    def _get_order_from_b2c_ref(self, b2c_ref, b2c_client, extended_domain=None):
        domain = self._get_base_search_domain(b2c_client)
        domain = expression.AND([domain, [("b2c_ref", "=", b2c_ref)]])
        if extended_domain:
            domain = expression.AND([domain, extended_domain])
        res = self.search(domain)
        if not res:
            msg = _("Sale order not found for id {b2c_ref}").format(b2c_ref=b2c_ref)
            _logger.error(msg)
            raise MissingError(msg)
        return res

    def _search_orders_from_b2c(
        self, b2c_refs: list, limit: int, offset: int, b2c_client
    ):
        domain = self._get_base_search_domain(b2c_client)
        if b2c_refs:
            domain = expression.AND([domain, [("b2c_ref", "in", b2c_refs)]])
        return self.search(domain, limit=limit, offset=offset)
