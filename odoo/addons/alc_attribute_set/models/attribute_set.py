# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.attribute_set.models.attribute_set import (
    AttributeSet as AttributeSetBase,
)


class AttributeSet(AttributeSetBase):
    # without this user like kplompteux can't browse attribute set on product
    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        return super(AttributeSet, self.sudo()).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
