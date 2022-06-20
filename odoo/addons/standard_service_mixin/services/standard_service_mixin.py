# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class ModelMixin(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "standard.service.mixin"

    def _get_schema_generator(self):
        raise NotImplementedError  # entrypoint

    @property
    def _schema_generator(self):
        if not getattr(self, "_schema_generator_", None):
            self._schema_generator_ = self._get_schema_generator()
        return self._schema_generator_

    def _get_schema(self, keyword, search=False):
        schema = {}
        schema_attrs = [
            "type",
            "allowed",
            "default",
            "required",
            "nullable",
            "coerce",
            "schema",
        ]
        for fn, field in self._schema_generator.items():
            if keyword not in field:
                continue
            operators = field.get("operators", ["="]) if search else ["="]
            for operator in operators:
                fn = fn if operator == "=" else "__".join((fn, operator))
                schema_fn = {}
                for a in schema_attrs:
                    f_a = self._field_attr(field, keyword, a)
                    if f_a is not None:
                        schema_fn[a] = f_a
                schema[fn] = schema_fn
        return schema

    def _search_param(self, field, keyword, param):
        param, operator = param.split("__")
        param = self._field_attr(field, keyword, "name") or param
        return param, (operator or "=")

    def _get_parser(self, keyword):
        parser = []
        for field in self._schema_generator.values():
            field_parser = self._field_attr(field, keyword, "parser")
            if field_parser:
                parser.append(field_parser)
        return parser

    def _field_attr(self, field_dict, keyword, attr):
        value = field_dict.get(keyword, {}).get(attr) or field_dict.get(attr)
        if attr == "type" and not value:
            raise ValueError("Type cannot be None.")
        return value

    def _get_base_domain(self, keyword):
        return []

    def _get_domain(self, keyword, params):
        domain = self._get_base_domain(keyword)
        ssg = self._schema_generator
        for param in params:
            if param in ssg and keyword in ssg[param]:
                fn, operator = self._search_param(ssg[param], keyword, param)
                domain.append((fn, operator, params[param]))
        return domain

    def _process_params(self, params, keyword):
        mappers = set()
        to_remove = set()
        for fn, field_dict in self._schema_generator.items():
            mapper = self._field_attr(field_dict, keyword, "map")
            if mapper:
                mappers.add(mapper)
                if not self._field_attr(field_dict, keyword, "mapper_keep"):
                    to_remove.add(fn)
        for mapper in mappers:
            fmapper = getattr(self, mapper)
            params = fmapper(params)
        for param in to_remove:
            params.pop(param, None)
        return params

    def _process_records(self, records, keyword):
        parser = self._get_parser(keyword)
        jsons = records.jsonify(parser)
        return [self._convert_one_record(keyword, r, j) for r, j in zip(records, jsons)]

    def _convert_one_record(self, keyword, record, j):
        return j
