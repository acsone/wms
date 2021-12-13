# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.shopfloor_base.utils import ensure_model


class DataDetailAction(Component):
    _inherit = "shopfloor.data.detail.action"

    @ensure_model("stock.picking")
    def pack_picking_detail(self, record, **kw):
        data = self.picking_detail(record, **kw)
        data["scanned_packs"] = list(record._packing_scanned_packs)
        return data
