# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, fields
from odoo.exceptions import AccessDenied

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


def date_parser(date_str):
    return fields.Date.from_string(date_str) if date_str else None


class ClassifiedService(Component):
    """Classified advertisments service.
       It allows to manage the lifecycle of a private ad (CRUD), and submit them.
       In Back-Office these can then be approved for publication, in which case
       they will appear in the search results of all authenticated partner.
       The rejection_reason and state are fields that are only used for private
       management.
    """

    _inherit = "authenticated_partner.mixin"
    _name = "classified.service"
    _collection = "shopinvader.backend"
    _usage = "classified_ads"

    def _get_categories(self):
        return [s[0] for s in self.model._fields["category"].selection]

    def _get_country_state_codes(self):
        domain = [("country_id", "=", self.env.ref("base.be").id)]
        states = self.env["res.country.state"].search(domain)
        return states.mapped("code")

    def _check_private_classified_access(self, classified):
        private = classified.partner_id == self.partner
        if not private and not classified.state == "published":
            raise AccessDenied(_("This classified ad cannot be retrieved."))

    @restapi.method(
        [(["/new_simple"], "POST")],
        input_param=restapi.CerberusValidator("_input_schema"),
        output_param=restapi.CerberusValidator("_output_private_schema"),
    )
    def new_simple(self, **params):
        """Private endpoint. Create a new draft ad, waiting for submission.
           Does not allow to submit a file, giving a simple input schema that
           is correctly serialized in Swagger.
        """
        params = self._process_params(params, create=True)
        classified = self.model.create(params)
        return {"size": 1, "data": self._to_json(private=True, records=classified)}

    @restapi.method(
        [(["/"], "POST")],
        input_param=restapi.MultipartFormData(
            {
                "file": restapi.BinaryData(mediatypes=["application/pdf"]),
                "parameters": restapi.CerberusValidator("_input_schema"),
            },
        ),
        output_param=restapi.CerberusValidator("_output_private_schema"),
    )
    def create_new(self, parameters=None, file=None):
        """Private endpoint. Create a new draft ad, waiting for submission."""
        params = parameters
        params = self._process_params(params, create=True)
        params = self._process_file(params, None, file, params["name"])
        classified = self.model.create(params)
        return {"size": 1, "data": self._to_json(private=True, records=classified)}

    @restapi.method(
        [(["/<int:_id>"], "DELETE")], output_param=restapi.CerberusValidator({})
    )
    def delete(self, _id):
        """Private endpoint. Delete an ad."""
        classified = self.model.browse(_id)
        self._check_private_classified_access(classified)
        classified.unlink()
        return {}

    @restapi.method(
        [(["/<int:_id>/submit"], "POST")], output_param=restapi.CerberusValidator({})
    )
    def submit(self, _id):
        """Private endpoint. Submit the ad for publication."""
        classified = self.model.browse(_id)
        self._check_private_classified_access(classified)
        classified.submit()
        return {}

    @restapi.method(
        [(["/<int:_id>/update_set_to_draft"], "POST")],
        input_param=restapi.MultipartFormData(
            {
                "file": restapi.BinaryData(mediatypes=["application/pdf"]),
                "parameters": restapi.CerberusValidator("_input_update_schema"),
            },
        ),
        output_param=restapi.CerberusValidator("_output_private_schema"),
    )
    def update_set_to_draft(self, _id, parameters, file=None):
        """Private endpoint. Allows to update any field and but unpublishes the ad."""
        params = parameters or {}
        params = self._process_params(params)
        classified = self.model.browse(_id)
        self._check_private_classified_access(classified)
        params = self._process_file(params, classified, file, classified.name)
        classified.update_set_to_draft(params)
        return {"size": 1, "data": self._to_json(private=True, records=classified)}

    @restapi.method(
        [(["/<int:_id>/update_set_to_pending"], "POST")],
        input_param=restapi.MultipartFormData(
            {
                "file": restapi.BinaryData(mediatypes=["application/pdf"]),
                "parameters": restapi.CerberusValidator("_input_update_schema"),
            },
        ),
        output_param=restapi.CerberusValidator("_output_private_schema"),
    )
    def update_set_to_pending(self, _id, parameters, file=None):
        """Private endpoint. Allows to update any field.
           It unpublishes the ad and directly resubmit it."""
        # same thing as update_set_to_draft, then submit
        params = parameters or {}
        params = self._process_params(params)
        classified = self.model.browse(_id)
        self._check_private_classified_access(classified)
        params = self._process_file(params, classified, file, classified.name)
        classified.update_set_to_pending(params)
        return {"size": 1, "data": self._to_json(private=True, records=classified)}

    @restapi.method(
        [(["/<int:_id>"], "GET")],
        output_param=restapi.CerberusValidator("_output_schema"),
    )
    def get(self, _id):
        """This endpoint returns all private fields iff it belongs to the partner,
           otherwise return all published fields. If the ad is not published or not
           accessible, access is denied.
        """
        classified = self.model.browse(_id)
        private = classified.partner_id == self.partner
        if not private and not classified.state == "published":
            raise AccessDenied(_("This classified ad cannot be retrieved."))
        return {"size": 1, "data": self._to_json(private=private, records=classified)}

    @restapi.method(
        [(["/search"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_output_schema"),
    )
    def search(self, **params):
        """Endpoint for published classified ads. Does not allow to filter on state."""
        params = self._process_params(params)
        domain = self._get_domain(private=False, params=params)
        return self._paginate_search(private=False, domain=domain, **params)

    @restapi.method(
        [(["/my_classified_ads"], "GET")],
        input_param=restapi.CerberusValidator("_search_private_input_schema"),
        output_param=restapi.CerberusValidator("_output_private_schema"),
    )
    def search_my_classifieds(self, **params):
        """Private endpoint. Allows to filter on state."""
        params = self._process_params(params)
        domain = self._get_domain(private=True, params=params)
        return self._paginate_search(private=True, domain=domain, **params)

    def _process_params(self, params, create=False):
        if create:
            params["partner_id"] = self.partner.id
        for date in ("from_date", "to_date"):
            if date in params and not isinstance(params[date], str):
                params[date] = fields.Datetime.to_string(params[date])
        state_code = params.pop("country_state_code", None)
        if state_code:
            params["state_id"] = self._state_code_to_state(state_code).id
        return params

    def _process_file(self, params, classified=None, file=None, name=None):
        if file:
            data = base64.encodestring(file.read())  # pylint: disable=deprecated-method
            f_name = self.env["alc.classified"]._get_filename(name)
            vals_new_file = {"name": "%s.pdf" % f_name, "data": data}
            new_file = self.env["mixin.file.id"]._create_file_id(vals_new_file)
            params["file_id"] = new_file.id
        if params.pop("file_delete", False) or file:
            if classified:
                classified.file_id.unlink()
                classified.file_id = False
        return params

    def _get_domain(self, private, params):
        state = params.pop("state", None)  # only acceptable in private!
        if private:
            domain = [("partner_id", "=", self.partner.id)]
            if state:
                domain.append(("state", "=", state))
        else:
            domain = [("state", "=", "published")]
        from_date = params.pop("from_date", None)
        if from_date:
            domain.append(("date_start", ">=", from_date))
        for param in ("category", "state_id"):
            if params.get(param):
                value = params.pop(param)
                domain.append((param, "=", value))
        for param in ("name", "body", "phone", "contact"):
            if params.get(param):
                value = params.pop(param)
                domain.append((param, "ilike", "%%%s%%" % value))
        return domain

    def _state_code_to_state(self, code):
        domain = [("code", "=", code), ("country_id", "=", self.env.ref("base.be").id)]
        state = self.env["res.country.state"].search(domain)
        state.ensure_one()
        return state

    def _get_parser(self, private):
        parser = self._get_base_parser()
        if private:
            parser += self._get_private_fields_parser()
        return parser

    def _get_base_parser(self):
        file_parser = (
            lambda r, fn: {
                "url": r.file_id.url,
                "name": r.file_id.name,
                "mimetype": r.file_id.mimetype or None,
            }
            if r.file_id
            else None
        )
        return [
            "id",
            "name",
            "body",
            "category",
            ("state_id:country_state", ["code", "name"]),
            "email",
            "contact",
            "phone",
            "date_start",
            "date_end",
            ("file", file_parser),
        ]

    def _get_private_fields_parser(self):
        return ["state", "rejection_reason"]

    def _search_private_input_schema(self):
        return self._search_input_schema(private=True)

    def _search_input_schema(self, private=False):
        schema = {
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
        }
        schema.update(self._input_schema(search=True, private=private))
        return schema

    def _state_schema(self, search=False, private=False):
        return {
            "type": "string",
            "required": not search and private,
            "nullable": False,
            "allowed": [s[0] for s in self.model._fields["state"].selection],
        }

    def _input_fields_schema(self, search=False, private=False):
        schema = {
            "country_state_code": self._get_country_code_schema(search=search),
            "file_delete": {"type": "boolean", "required": False},
        }
        if private:
            schema["state"] = self._state_schema(search=search)
        if search:
            schema["from_date"] = {
                "type": "date",
                "required": False,
                "nullable": False,
                "coerce": date_parser,
            }
        return schema

    def _output_fields_schema(self, private=False):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "country_state": {
                "type": "dict",
                "schema": self._get_country_state_schema(),
            },
            "file": {
                "type": "dict",
                "required": False,
                "nullable": True,
                "schema": {
                    "name": {"type": "string", "required": True},
                    "url": {"type": "string", "required": True},
                    "mimetype": {"type": "string", "required": True, "nullable": True},
                },
            },
            "state": self._state_schema(private=private),
            "rejection_reason": {"type": "string", "required": False, "nullable": True},
        }

    def _common_fields_schema(self, search=False):
        required = not search
        schema = {
            "name": {"type": "string", "required": required, "nullable": False},
            "body": {"type": "string", "required": required, "nullable": False},
            "phone": {"type": "string", "required": required, "nullable": False},
            "contact": {"type": "string", "required": required, "nullable": False},
            "email": {"type": "string", "required": required, "nullable": False},
            "category": {
                "type": "string",
                "required": required,
                "allowed": self._get_categories(),
            },
        }
        if not search:
            dtt = {
                "type": "date",
                "required": True,
                "nullable": False,
                "coerce": date_parser,
            }
            schema["date_start"] = dtt
            schema["date_end"] = dtt
        return schema

    def _get_country_code_schema(self, search=False):
        return {
            "type": "string",
            "allowed": self._get_country_state_codes(),
            "required": not search,
            "nullable": False,
        }

    def _get_country_state_schema(self):
        return {
            "name": {"type": "string", "required": True, "nullable": False},
            "code": self._get_country_code_schema(),
        }

    def _get_output_model_schema(self, private=False):
        schema = self._common_fields_schema()
        schema.update(self._output_fields_schema(private=private))
        return schema

    def _output_schema(self, private=False):
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": self._get_output_model_schema(private=private),
                },
            },
        }

    def _output_private_schema(self):
        return self._output_schema(private=True)

    def _input_schema(self, search=False, private=False):
        schema = self._common_fields_schema(search=search)
        schema.update(self._input_fields_schema(search=search, private=private))
        return schema

    def _input_update_schema(self):
        schema = self._input_schema()
        for field in schema:
            schema[field]["required"] = False
        return schema

    @property
    def model(self):
        return self.env["alc.classified"]

    def _paginate_search(self, private, domain, page=1, per_page=10):
        total_count = self.model.search_count(domain)
        offset = per_page * (page - 1)
        records = self.model.search(domain, limit=per_page, offset=offset)
        return {"size": total_count, "data": self._to_json(private, records)}

    def _to_json(self, private, records):
        parser = self._get_parser(private)
        return records.jsonify(parser)
