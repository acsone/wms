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

    @api.model
    def _update_b2c_recipient(self, b2c_id, b2c_backend, data):
        """ Update the final customer
        """
        b2c_ref = self._b2c_id_to_b2c_ref(b2c_id, b2c_backend)
        partner = self._get_partner_by_ref(b2c_ref)
        country_id = None
        country_code = data.get("country_code")
        if country_code:
            country_id = self.env["res.country"]._get_by_code(country_code).id

        name = data.get("first_name")
        last_name = data.get("last_name")
        if last_name:
            name = u"{} {}".format(name, last_name)
        title = data.get("title")
        if title:
            title = self.env.ref(TITLE_XML_ID_BY_B2C_KEY[title]).id

        partner.write(
            {
                "title": title if title else partner.title.id,
                "name": name if name else partner.name,
                "street": data.get("street") if data.get("street") else partner.street,
                "street2": data.get("street2")
                if data.get("street2")
                else partner.street2,
                "zip": data.get("zip") if data.get("zip") else partner.zip,
                "city": data.get("city") if data.get("city") else partner.city,
                "phone": data.get("phone") if data.get("phone") else partner.phone,
                "mobile": data.get("mobile") if data.get("mobile") else partner.mobile,
                "country_id": country_id if country_id else partner.country_id,
            }
        )

        return partner

    @api.model
    def _get_partner_by_ref(self, b2c_ref, raise_if_notfound=True):
        partner = self.search([("ref", "=", b2c_ref)], order="parent_id desc", limit=1,)
        if not partner and raise_if_notfound:
            raise ValidationError(_("No match found for customer_id: %s") % b2c_ref)
        return partner

    @api.model
    def _b2c_id_to_b2c_ref(self, _id, b2c_backend):
        return u"{}_{}".format(b2c_backend.sale_channel, _id)

    @api.model
    def _b2c_ref_to_b2c_id(self, ref):
        return ref.split("_")[1]
