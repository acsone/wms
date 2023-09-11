# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopfloorSchemaAction(Component):

    _inherit = "shopfloor.schema.action"

    def product(self):
        schema_product = super().product()
        schema_product.update(
            {"image": {"type": "string", "nullable": True, "required": False}}
        )
        return schema_product
