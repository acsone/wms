# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class PaginatedServiceMixin(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "paginated.service.mixin"

    def _paginated_search(self, domain, page, per_page):
        count = self.model.search_count(domain)
        offset = per_page * (page - 1)
        records = self.model.search(domain, limit=per_page, offset=offset)
        return count, records

    def _paginate_result(self, count, data):
        return {"size": count, "data": data}

    def _paginate_schema(self, schema):
        return {
            "size": {"type": "integer"},
            "data": {"type": "list", "schema": {"type": "dict", "schema": schema}},
        }
