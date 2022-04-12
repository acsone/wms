# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from werkzeug.exceptions import NotFound

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class FormService(Component):
    _inherit = "authenticated_partner.mixin"
    _name = "form.service"
    _collection = "shopinvader.backend"
    _usage = "form"

    @restapi.method(
        [(["/"], "GET")],
        output_param=restapi.CerberusValidator("_search_output_schema"),
        auth="public_or_default",
    )
    def search(self, **params):
        return self._search()

    @restapi.method(
        [(["/<int:form_id>"], "POST")],
        input_param=restapi.CerberusValidator("_submit_input_schema"),
        output_param=restapi.CerberusValidator("_submit_output_schema"),
        auth="public_or_default",
    )
    def submit(self, form_id, **params):
        form = self.env["alc.eshop.form"].sudo().browse(form_id).exists()
        if not form:
            raise NotFound("No form found for id")
        form._send_collected_info(params.get("data"), self.partner)
        return {"status": "OK"}

    ############
    # validators
    ############
    def _search_output_schema(self):
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._form_schema},
            },
        }

    def _submit_input_schema(self):
        return {
            "data": {
                "meta": {
                    "description": "A key / value mapping ",
                    "example": {"name": "Mrs B"},
                },
                "type": "dict",
                "required": True,
                "nullable": True,
                "keysrules": {"type": "string"},
                "valuesrules": {"type": "string", "required": True, "nullable": False},
            }
        }

    def _submit_output_schema(self):
        return {"status": {"type": "string", "required": False, "allowed": ["OK"]}}

    @property
    def _form_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "name": {"type": "string", "required": True, "nullable": False},
            "form": {"type": "string", "required": True, "nullable": False},
            "form_options": {"type": "string", "required": True, "nullable": False},
            "sequence": {"type": "integer", "required": True, "nullable": False},
        }

    ################
    # implementation
    ################
    def _search(self):
        audience = "authenticated_only" if self.partner else "public_only"
        forms = (
            self.env["alc.eshop.form"]
            .sudo()
            .search([("audience", "=", audience), ("published", "=", True)])
        )
        return {
            "size": len(forms),
            "data": [self._form_to_json(f) for f in forms],
        }

    def _form_to_json(self, form):
        return dict(
            id=form.id,
            name=form.name,
            form=form.form,
            form_options=form.form_options,
            sequence=form.sequence,
        )
