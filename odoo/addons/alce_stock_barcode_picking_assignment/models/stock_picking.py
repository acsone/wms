# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV

from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "barcodes.barcode_events_mixin"]

    def on_barcode_scanned(self, barcode):
        """ Try to assign the operator if not yet assigned and barcode is
        an operator
        """
        if not self.operator_id:
            user = self.env["res.users"].get_user(barcode.replace("U#", ""))
            if user:
                self.operator_id = user
                return None
            raise UserError(_("Please start operation first"))

        return super(StockPicking, self).on_barcode_scanned(barcode)
