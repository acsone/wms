# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _get_put_in_pack_package(self, operations):
        package = self.env["stock.quant.package"]
        if (
            self.picking_type_subcode != "PICK"
            and self.picking_type_code == "outgoing"
            and self.delivery_type == "gls"
        ):
            pack_operation_candidates = self.pack_operation_ids.browse()
            for op in (o for o in operations if not o.result_package_id):
                pack_operation_candidates |= op
            package = pack_operation_candidates.mapped("package_id")
            if len(package) > 1:
                raise ValidationError(_("More than one pack"))
        return package or super(StockPicking, self)._get_put_in_pack_package(operations)
