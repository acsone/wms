# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tools import drop_index, index_exists

from odoo.addons.shopfloor_workstation.models import shopfloor_workstation


class ShopfloorWorkstation(shopfloor_workstation.ShopfloorWorkstation):

    barcode = fields.Char(index=False)

    def init(self):  # pylint: disable=missing-return
        super().init()
        if index_exists(
            self._cr,
            "shopfloor_workstation_barcode_unique",
        ):
            # covered by the previous index
            drop_index(
                self._cr, "shopfloor_workstation_barcode_index", "shopfloor_workstation"
            )
