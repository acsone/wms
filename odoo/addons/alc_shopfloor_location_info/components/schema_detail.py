# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopfloorSchemaDetailAction(Component):
    _inherit = "shopfloor.schema.detail.action"

    def location_detail(self):
        schema = super(ShopfloorSchemaDetailAction, self).location_detail()
        schema.update(
            {
                "reserved_operations": self._schema_list_of(self.operation()),
                "products": self._schema_list_of(self.location_product()),
            }
        )
        return schema

    def location_product(self):
        schema = self.product()
        schema.update(
            {
                "quantity": {"type": "float", "required": True},
                "lots": self._schema_list_of(self.location_lot()),
            }
        )
        return schema

    def location_lot(self):
        schema = self.lot()
        schema.update(
            {
                "removal_date": {"type": "string", "nullable": True, "required": False},
                "expire_date": {"type": "string", "nullable": True, "required": False},
                "quantity": {"type": "float", "required": True},
            }
        )
        return schema
