# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ElasticsearchAdapter(Component):
    _inherit = "elasticsearch.adapter"

    def put_info_banners(self, banners):
        lang = self.work.index.lang_id
        banners.invalidate_cache(["html"])
        banners = banners.with_context(lang=lang.code)
        self.index(banners.mapped("json_doc"))
