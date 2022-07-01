# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.shopfloor_base.utils import ensure_model


class DataDetailAction(Component):
    _inherit = "shopfloor.data.detail.action"

    @ensure_model("stock.picking")
    def pack_picking_detail(self, record, **kw):
        return {
            "id": record.id,
            "name": record.name,
            "partner": {"id": record.partner_id.id, "name": record.partner_id.name},
            "scanned_packs": list(record._packing_scanned_packs),
            "operations": [
                self._pack_picking_operation_detail(op)
                for op in record.pack_operation_ids
            ],
        }

    def _pack_picking_operation_detail(self, record):
        return {
            "id": record.id,
            "qty_done": record.qty_done,
            "product": self.product(
                record.product_id or record.package_id.single_product_id
            ),
            "package_src": self.package(record.package_id, record.picking_id),
            "package_dest": self.package(record.result_package_id, record.picking_id),
        }
