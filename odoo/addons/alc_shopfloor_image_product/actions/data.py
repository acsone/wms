# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class DataAction(Component):
    _inherit = "shopfloor.data.action"

    def _product_image_url(self, record, field_name):
        return record[field_name] or None

    @property
    def _product_parser(self):
        return super(DataAction, self)._product_parser + [
            ("image_medium_url:image", self._product_image_url)
        ]
