# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.models import ir_attachment
from odoo.addons.fs_image.fields import FSImageValue


class IrAttachment(ir_attachment.IrAttachment):
    def _get_or_create_thumbnail(self):
        self.ensure_one()
        thumbnail = self.thumbnail_ids.filtered(
            lambda t, name=self.name: t.base_name == name
        )
        if not thumbnail:
            thumbnail = self.thumbnail_ids.create(
                {
                    "attachment_id": self.id,
                    "base_name": self.name,
                    "image": FSImageValue(name=self.name, value=self.raw),
                    "size_x": "999",
                    "size_y": "999",
                }
            )
        return thumbnail
