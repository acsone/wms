# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.attribute_set.models.attribute_set_owner import (
    AttributeSetOwnerMixin as AttributeSetOwnerMixinBase,
)


class AttributeSetOwnerMixin(AttributeSetOwnerMixinBase):
    @api.model
    def _build_attribute_eview(self):
        return super(
            AttributeSetOwnerMixin, self.with_context(include_native_attribute=True)
        )._build_attribute_eview()
