# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ElasticsearchAdapter(Component):
    _inherit = "elasticsearch.adapter"

    def put_ads(self, ads):
        lang = self.work.index.lang_id
        ads = ads.filtered(lambda a, lang=lang: not a.lang_id or a.lang_id == lang)
        self.index(ads.mapped("json_doc"))
