# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import mimetypes

from odoo import _, fields
from odoo.exceptions import MissingError
from odoo.http import content_disposition, request

from odoo.addons.alc_cerberus_utils import utils
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class DocumentService(Component):
    """Manage subscription to product's promotions."""

    _inherit = "base.rest.service"
    _name = "document.service"
    _collection = "shopinvader.backend"
    _usage = "documents"

    def _get_types(self):
        return [s[0] for s in self.model._fields["type"].selection]

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search(self, **params):
        document_type = params.pop("type", None)
        for date in ("from_date", "to_date"):
            if date in params and not isinstance(params[date], str):
                params[date] = fields.Datetime.to_string(params[date])
        domain = self._get_base_domain()
        if document_type:
            domain.append(("type", "=", document_type))
        from_date = params.pop("from_date", None)
        if from_date:
            domain.append(("document_date", ">=", from_date))
        to_date = params.pop("to_date", None)
        if to_date:
            domain.append(("document_date", "<=", to_date))
        return self._paginate_search(domain, **params)

    @restapi.method(
        routes=[(["/<int:_id>/download"], "GET")],
        output_param=restapi.BinaryData(required=True),
    )
    def download(self, _id):
        target = self._get(_id)
        headers, content = self._get_binary_content(target)
        if not content:
            raise MissingError(_("No content found for %s") % _id)
        response = request.make_response(content, headers)
        response.status_code = 200
        return response

    ############
    # validators
    ############
    def _search_input_schema(self):
        return {
            "page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 1,
            },
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 10,
            },
            "type": {
                "type": "string",
                "allowed": self._get_types(),
                "required": False,
                "nullable": True,
            },
            "from_date": {
                "type": "datetime",
                "required": False,
                "nullable": False,
                "coerce": utils.isoformat_str_dt_to_dt_utc,
            },
            "to_date": {
                "type": "datetime",
                "required": False,
                "nullable": False,
                "coerce": utils.isoformat_str_dt_to_dt_utc,
            },
        }

    def _get_model_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "name": {"type": "string", "required": True, "nullable": False},
            "type": {"type": "string", "required": True, "nullable": True},
            "res_model": {"type": "string", "required": False, "nullable": True},
            "format": {"type": "string", "required": True, "nullable": True},
            "sale_channel": {
                "type": "string",
                "required": False,
                "nullable": True,
                "allowed": self.env["sale.order"]._get_sale_channels_internal(),
            },
            "document_date": {"type": "datetime", "required": False, "nullable": True},
        }

    def _search_output_schema(self):
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._get_model_schema()},
            },
        }

    ################
    # implementation
    ################

    @property
    def env(self):
        env = self.work.env
        return env

    @property
    def model(self):
        return self.env["alc.document"]

    @property
    def partner(self):
        partner = self.env["res.partner"].browse()
        partner_id = self.work.authenticated_partner_id
        if partner_id:
            partner = partner.browse(partner_id)
        return partner

    def _get_base_domain(self):
        return self.model.get_partner_domain(self.partner)

    def _get(self, _id):
        domain_base = self._get_base_domain()
        domain = domain_base + [("id", "=", _id)]
        return self.model.search(domain)

    def _paginate_search(self, domain, page=1, per_page=10):
        total_count = self.model.search_count(domain)
        offset = per_page * (page - 1)
        records = self.model.search(domain, limit=per_page, offset=offset)
        return {"size": total_count, "data": self._to_json(records)}

    def _to_json(self, records):
        return [self._convert_one_record(record) for record in records]

    def _convert_one_record(self, record):
        record.ensure_one()
        values = record.jsonify(self._get_model_schema().keys(), one=True)
        # jsonify convert string to string with tzinfo...
        # cerberus validator requires datetime for date and datetime fields
        # Since the jsonencoder into base_rest will convert dt into isoformat
        # at serialization, it's possible to keep a dt into our message
        # to allow cerberus to validate the data.
        values["document_date"] = utils.odoo_str_dt_to_dt_utc(record.document_date)
        return values

    def _get_binary_content(self, target):
        content = target._get_data()
        content = base64.b64decode(content) if content else ""
        mimetype_guess = mimetypes.guess_type(target.name)
        mimetype = mimetype_guess[0] if mimetype_guess else mimetype_guess
        headers = [
            ("Content-Type", mimetype),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Disposition", content_disposition(target.name)),
            ("Content-Length", len(content)),
        ]
        return headers, content
