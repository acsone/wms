# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.alc_partner_type.models.res_partner import ResPartner as ResPartnerBase

from .alc_b2c_client import AlcB2cClient

_logger = logging.getLogger(__name__)

TITLE_XML_ID_BY_B2C_KEY = {
    "mr": "base.res_partner_title_mister",
    "mm": "base.res_partner_title_madam",
}


class ResPartner(ResPartnerBase):
    alc_b2c_client_id = fields.Many2one[AlcB2cClient](readonly=True)

    @api.depends("partner_type", "is_b2c_customer")
    def _compute_is_student(self):
        """The student category is also used as a miscellaneous category."""
        res = super()._compute_is_student()
        for partner in self.filtered(lambda p: p.is_student and p.is_b2c_customer):
            partner.is_student = False
        return res

    def _update_b2c_recipient_validate_data(self, data, b2c_client):
        """If this partner has one started picking out, only update contact fields."""
        self.ensure_one()
        domain_pickings = [
            ("customer_id", "=", self.id),
            ("picking_type_code", "=", "outgoing"),
            ("printed", "=", True),
        ]
        keys = ["mobile", "phone", "email", "comment", "name2"]
        if (
            self.env["stock.picking"].search(domain_pickings, limit=1)
            and not b2c_client.allow_customer_modifications
        ):
            for key in data:
                value = self[key].id if key in {"title", "country_id"} else self[key]
                if key not in keys and data[key] != value and (data[key] or value):
                    _logger.error(
                        "You cannot update this address since there are already"
                        " closed Sale Orders for this partner. "
                        "Incoherent field: %s, current value: %s",
                        key,
                        value,
                    )
                    msg = _(
                        "You cannot update this address since there are already"
                        " closed Sale Orders for this partner. "
                        "Incoherent field: {key}, current value: {value}"
                    ).format(key=key, value=value)
                    raise ValidationError(msg)
        return data

    @api.model
    def _update_b2c_recipient(self, b2c_id, b2c_client, data):
        """Update the final customer."""
        b2c_ref = self._b2c_id_to_b2c_ref(b2c_id, b2c_client)
        partner = self._get_partner_by_ref(b2c_ref)
        partner._update_b2c_data(data, b2c_client)
        return partner

    def _update_b2c_data(self, data, b2c_client):
        self.ensure_one()
        data.pop("id", None)
        if data.get("country_code"):
            country = self.env["res.country"]._get_by_code(data.pop("country_code"))
            data["country_id"] = country.id
        name = data.pop("first_name", "")
        if data.get("last_name"):
            name = f"{name} {data.pop('last_name')}"
        if name:
            data["name"] = name
        if data.get("title"):
            data["title"] = self.env.ref(TITLE_XML_ID_BY_B2C_KEY[data["title"]]).id
        if "name2" in data:
            data["suite"] = data.pop("name2")
        if "note" in data:  # passing None is allowed, so no get here
            data["comment"] = data.pop("note")
        self._update_b2c_recipient_validate_data(data, b2c_client)
        return self.write(data)

    @api.model
    def _get_partner_by_ref(self, b2c_ref, raise_if_notfound=True):
        partner = self.search(
            [("ref", "=", b2c_ref)],
            order="parent_id desc",
            limit=1,
        )
        if not partner and raise_if_notfound:
            msg = _("No match found for customer_id: {b2c_ref}").format(b2c_ref=b2c_ref)
            _logger.error(msg)
            raise ValidationError(msg)
        return partner

    @api.model
    def _b2c_id_to_b2c_ref(self, b2c_id, b2c_client):
        return f"{b2c_client.sale_channel_id.code}_{b2c_id}"

    @api.model
    def _b2c_ref_to_b2c_id(self, ref):
        return ref.split("_")[1] if isinstance(ref, str) else None

    @api.model
    def _prepare_b2c_partner_values(self, data, b2c_client):
        b2c_ref = self.env["res.partner"]._b2c_id_to_b2c_ref(data["id"], b2c_client)
        name = data["first_name"]
        last_name = data.get("last_name")
        if last_name:
            name = f"{name} {last_name}"
        title = data.get("title")
        if title:
            title = self.env.ref(TITLE_XML_ID_BY_B2C_KEY[title]).id
        country_id = None
        country_code = data.get("country_code")
        if country_code:
            country_id = self.env["res.country"]._get_by_code(country_code).id
        return {
            "alc_b2c_client_id": b2c_client.id,
            "name": name,
            "title": title,
            "email": data.get("email"),
            "street": data.get("street"),
            "street2": data.get("street2"),
            "zip": data.get("zip"),
            "city": data.get("city"),
            "phone": data.get("phone"),
            "mobile": data.get("mobile"),
            "sale_reason_backorder_strategy": b2c_client.sale_reason_backorder_strategy,
            "is_b2c_customer": True,
            "partner_type": "student_like",
            "ref": b2c_ref,
            "country_id": country_id,
            "suite": data.get("name2"),
            "comment": data.get("note"),
        }

    @api.model
    def _create_b2c_partner(self, data, b2c_client):
        return self.create(self._prepare_b2c_partner_values(data, b2c_client))
