# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma.models.rma import Rma as RmaBase


class Rma(RmaBase):
    def _create_receipt(self):
        res = super()._create_receipt()
        if self.move_id.picking_type_id.empty_package_at_return:
            move_lines = self.reception_move_id.picking_id.move_line_ids
            move_lines.result_package_id = False
        return res
