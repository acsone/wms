# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api
from odoo.exceptions import ValidationError

from odoo.addons.alc_b2c_connector.models.sale_order import SaleOrder as Order


class SaleOrder(Order):
    @api.model
    def _b2c_carriers(self):
        return {
            "GLS_BE": "alc_delivery_carrier_gls.delivery_carrier_gls_be",
            "ALCYON": "__setup__.deliver_carrier_alcyon",  # TODO: put in a module :-/
        }

    @api.model
    def _carriers_to_b2c(self, carrier):
        carriers = self._b2c_carriers()
        carrier_xmlids = carrier.get_external_id().values()
        carrier_keys = [k for k, v in carriers.items() if v in carrier_xmlids]
        return carrier_keys[0] if carrier_keys else carrier.name if carrier else None

    @api.model
    def _parse_b2c_order(self, data, b2c_backend):
        logiweb_channel = self.env.ref("alc_logiweb.sale_channel_logiweb")
        order_data = super()._parse_b2c_order(data, b2c_backend)
        if b2c_backend.sale_channel_id != logiweb_channel:
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

    def _prepare_update_recipient_from_b2c_vals(self, partner):
        vals = super()._prepare_update_recipient_from_b2c_vals(partner)
        belgium = self.env.ref("base.be")
        logiweb_channel = self.env.ref("alc_logiweb.sale_channel_logiweb")
        logiweb_partner = self.env.ref("alc_logiweb.logiweb_partner")
        logiweb_be_partner = self.env.ref("alc_logiweb.logiweb_be_partner")
        if (
            self.sale_channel_id == logiweb_channel
            and self.carrier_id.delivery_type == "gls"
            and self.partner_shipping_id != partner
        ):
            vals["partner_shipping_id"] = partner.id
        if (
            self.sale_channel_id == logiweb_channel
            and self.carrier_id.delivery_type == "gls"
        ):
            vals["partner_invoice_id"] = (
                logiweb_be_partner
                if partner.country_id == belgium
                else logiweb_partner.id
            )
        if (
            self.sale_channel_id == logiweb_channel
            and self.carrier_id.delivery_type == "fixed"
        ):  # no change for shipping
            vals["partner_shipping_id"] = self.partner_shipping_id.id
        return vals

    @api.constrains("sale_channel_id", "partner_id", "partner_invoice_id")
    def _check_b2c_order_invoice_address(self):
        ref = self.env.ref
        belgium = ref("base.be")
        logiweb_channel = ref("alc_logiweb.sale_channel_logiweb")
        for order in self.filtered(lambda o: o.sale_channel_id == logiweb_channel):
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
