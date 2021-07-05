# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, models
from odoo.exceptions import ValidationError

TITLE_XML_ID_BY_B2C_KEY = {
    "mr": "base.res_partner_title_mister",
    "mm": "base.res_partner_title_madam",
}


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _update_b2c_recipient_validate_data(self, data):
        """If this partner has one closed sale, only allow update of contact fields."""
        self.ensure_one()
        domain_orders = [("partner_id", "=", self.id), ("state", "=", "done")]
        if self.env["sale.order"].search(domain_orders, limit=1):
            for key in data:
                if key not in ("mobile", "phone", "email") and data[key] != self[key]:
                    msg = _(
                        "You cannot update this address since there are already"
                        " closed Sale Orders for this partner. "
                        "Incoherent field: %s, current value: %s"
                    )
                    raise ValidationError(msg % (key, self[key]))

    @api.model
    def _update_b2c_recipient(self, b2c_id, b2c_backend, data):
        """ Update the final customer
        """
        data.pop("id", None)
        b2c_ref = self._b2c_id_to_b2c_ref(b2c_id, b2c_backend)
        partner = self._get_partner_by_ref(b2c_ref)
        partner._update_b2c_data(data)
        return partner

    def _update_b2c_data(self, data):
        self.ensure_one()
        if data.get("country_code"):
            country = self.env["res.country"]._get_by_code(data.pop("country_code"))
            data["country_id"] = country.id
        name = data.pop("first_name", "")
        if data.get("last_name"):
            name = u"{} {}".format(name, data.pop("last_name"))
        if name:
            data["name"] = name
        if data.get("title"):
            data["title"] = self.env.ref(TITLE_XML_ID_BY_B2C_KEY[data["title"]]).id
        self._update_b2c_recipient_validate_data(data)
        return self.write(data)

    @api.model
    def _get_partner_by_ref(self, b2c_ref, raise_if_notfound=True):
        partner = self.search([("ref", "=", b2c_ref)], order="parent_id desc", limit=1,)
        if not partner and raise_if_notfound:
            raise ValidationError(_("No match found for customer_id: %s") % b2c_ref)
        return partner

    @api.model
    def _b2c_id_to_b2c_ref(self, b2c_id, b2c_backend):
        return u"{}_{}".format(b2c_backend.sale_channel, b2c_id)

    @api.model
    def _b2c_ref_to_b2c_id(self, ref):
        return ref.split("_")[1]
