# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class RecipientsService(Component):
    """
    Recipients services.

    Provides method to update recipient infos.

    """

    _inherit = "base.b2c.rest.service"
    _name = "recipients.service"
    _usage = "recipients"

    def update(self, _id, **params):
        partner = (
            self.env["res.partner"]
            .suspend_security()
            ._update_b2c_recipient(_id, self.b2c_backend, params)
        )
        return self._partner_to_json(partner[0])

    def _partner_to_json(self, partner):
        title = None
        if partner.title:
            if partner.title.name == "Madam":
                title = "mm"
            else:
                title = "mr"

        res = {
            "id": self.env["res.partner"]._b2c_ref_to_b2c_id(partner.ref),
            "title": title if title else "",
            "name": partner.name,
            "street": partner.street if partner.street else None,
            "street2": partner.street2 if partner.street2 else None,
            "zip": partner.zip if partner.zip else None,
            "city": partner.city if partner.city else None,
            "email": partner.email,
            "mobile": partner.mobile if partner.mobile else None,
            "country_code": partner.country_id.code if partner.country_id else None,
        }
        return res

    def _validator_update(self):
        return {
            "id": {"type": "string", "nullable": False, "required": True},
            "title": {
                "type": "string",
                "nullable": False,
                "required": False,
                "allowed": ["mr", "mm"],
            },
            "first_name": {"type": "string", "nullable": False, "required": False},
            "last_name": {"type": "string", "nullable": False, "required": False},
            "street": {"type": "string", "nullable": True, "required": False},
            "street2": {"type": "string", "nullable": True, "required": False},
            "zip": {"type": "string", "nullable": True, "required": False},
            "city": {"type": "string", "nullable": True, "required": False},
            "email": {"type": "string", "nullable": False, "required": False},
            "phone": {"type": "string", "nullable": True, "required": False},
            "mobile": {"type": "string", "nullable": True, "required": False},
            "country_code": {
                "type": "string",
                "nullable": True,
                "allowed": self.env["res.country"]._get_codes(),
            },
        }

    def _validator_return_update(self):
        return {
            "id": {"type": "string", "nullable": False, "required": True},
            "title": {
                "type": "string",
                "nullable": False,
                "required": False,
                "allowed": ["mr", "mm"],
            },
            "name": {"type": "string", "nullable": False, "required": True},
            "street": {"type": "string", "nullable": True, "required": False},
            "street2": {"type": "string", "nullable": True, "required": False},
            "zip": {"type": "string", "nullable": True, "required": False},
            "city": {"type": "string", "nullable": True, "required": False},
            "email": {"type": "string", "nullable": False, "required": True},
            "phone": {"type": "string", "nullable": True, "required": False},
            "mobile": {"type": "string", "nullable": True, "required": False},
            "country_code": {
                "type": "string",
                "nullable": True,
                "allowed": self.env["res.country"]._get_codes(),
            },
        }
