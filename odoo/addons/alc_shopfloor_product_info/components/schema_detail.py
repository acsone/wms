# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopfloorSchemaDetailAction(Component):
    _inherit = "shopfloor.schema.detail.action"

    def product_detail(self):
        schema = super(ShopfloorSchemaDetailAction, self).product_detail()
        schema.update({"locations": self._schema_list_of(self.location_detail())})
        return schema
