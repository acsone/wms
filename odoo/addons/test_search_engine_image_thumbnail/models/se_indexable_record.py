# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tools

from odoo.addons.search_engine_image_thumbnail.models.se_indexable_record import (
    SeIndexableRecord as SeIndexableRecordBase,
)


class SeIndexableRecord(SeIndexableRecordBase):
    def _get_thumbnail_sizes_by_size_for_field(self, index, field_name):
        self.ensure_one()
        sizes = index._get_thumbnail_sizes(field_name)
        if not sizes and tools.config["test_enable"]:
            return {}
        return super()._get_thumbnail_sizes_by_size_for_field(index, field_name)
