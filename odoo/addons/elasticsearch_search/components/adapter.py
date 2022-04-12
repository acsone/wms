# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from elasticsearch_dsl import Search

from odoo.addons.component.core import Component


class ElasticsearchAdapter(Component):
    _inherit = "elasticsearch.adapter"

    def search(self, es_params=None, params=None):
        """ES params should be a dict of the form {query, source, params}"""
        es_params = es_params or {}
        client = self._get_es_client()
        search = Search(using=client, index=self._index_name)
        for param in es_params or {}:
            fn = getattr(search, param)
            search = fn(es_params[param])
        if params:
            search = search.params(**params)
        return [hit.to_dict() for hit in search.scan()]
