# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _get_sale_channels_external_selection(self):
        res = super(SaleOrder, self)._get_sale_channels_external_selection()
        res.append(("logiweb", "Logiweb"))
        return res

    @api.model
    def _b2c_carriers(self):
        return {
            "GLS_BE": "alc_delivery_carrier_gls.delivery_carrier_gls_be",
            "ALCYON": "__setup__.deliver_carrier_alcyon",  # TODO: put in a module :-/
        }

    @api.model
    def _carriers_to_b2c(self, carrier):
        carriers = self._b2c_carriers()
        carrier_xmlids = carrier.get_xml_id().values()
        carrier_keys = [k for k in carriers if carriers[k] in carrier_xmlids]
        return carrier_keys[0] if carrier_keys else carrier.name if carrier else None

    @api.model
    def _parse_b2c_order(self, data, b2c_backend):
        order_data = super(SaleOrder, self)._parse_b2c_order(data, b2c_backend)
        if b2c_backend.sale_channel != "logiweb":
            return order_data
        carrier_key = data.get("carrier")
        if not carrier_key:
            raise ValidationError(_("Missing carrier"))
        carrier = self.env.ref(self._b2c_carriers()[carrier_key])
        order_data["carrier_id"] = carrier.id
        if data.get("gls_parcel_shop"):
            if carrier.delivery_type != "gls":
                msg = _("Cannot have a gls_parcel_shop if the delivery is not GLS.")
                raise ValidationError(msg)
            order_data["gls_parcel_shop"] = data["gls_parcel_shop"]
        if carrier.delivery_type == "gls":
            # the shipping address must be the final customer
            order_data["partner_shipping_id"] = order_data["partner_id"]
        return order_data

    def _update_recipient_from_b2c(self, partner):
        res = super(SaleOrder, self)._update_recipient_from_b2c(partner)
        if (
            self.sale_channel == "logiweb"
            and self.carrier_id.delivery_type == "gls"
            and self.partner_shipping_id != partner
        ):
            self.partner_shipping_id = partner
        return res

    @api.constrains("sale_channel", "partner_id", "partner_invoice_id")
    def _check_b2c_order_invoice_address(self):
        ref = self.env.ref
        belgium = ref("base.be")
        for order in self.filtered(lambda o: o.sale_channel == "logiweb"):
            belgian = order.partner_id.country_id == belgium
            invoicing = order.partner_invoice_id
            carrier_type = order.carrier_id.delivery_type
            carrier_type_gls = carrier_type == "gls"
            carrier_type_alcyon = carrier_type == "fixed"
            if (
                belgian
                and invoicing != ref("alc_logiweb.logiweb_be_partner")
                and carrier_type_gls
            ):
                msg = _("The invoicing partner should be Logiweb Belgium.")
                raise ValidationError(msg)
            if (
                not belgian
                and invoicing != ref("alc_logiweb.logiweb_partner")
                and carrier_type_gls
            ):
                raise ValidationError(_("The invoicing partner should be Logiweb."))
            if (
                invoicing == ref("alc_logiweb.logiweb_be_partner")
                and carrier_type_alcyon
            ):
                msg = _("The carrier 'Alcyon' is not allowed for Logiweb Belgium.")
                raise ValidationError(msg)
