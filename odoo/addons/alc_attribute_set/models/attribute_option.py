# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.attribute_set.models.attribute_option import (
    AttributeOption as AttributeOptionBase,
)


class AttributeOption(AttributeOptionBase):
    # without thisuser like kplompteux can't open a product
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        return super(AttributeOption, self.sudo()).fields_get(allfields, attributes)
