# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.attribute_set.models.attribute_attribute import (
    AttributeAttribute as AttributeAttributeBase,
)


class AttributeAttribute(AttributeAttributeBase):
    def _get_native_field_context(self):
        context = self.env[self.field_id.model]._fields[self.field_id.name].context
        return str(
            {
                k: v(self.env[self.field_id.model]) if callable(v) else v
                for k, v in context.items()
            }
        )
