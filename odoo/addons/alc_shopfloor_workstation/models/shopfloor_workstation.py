# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopfloorWorkstation(models.Model):

    _inherit = "shopfloor.workstation"

    printing_product_label_printer_id = fields.Many2one(
        comodel_name="printing.printer", string="Product Label Printer"
    )

    def set_as_default_on_user(self, user):
        res = super(ShopfloorWorkstation, self).set_as_default_on_user(user)
        if self.printing_product_label_printer_id:
            user.printing_product_label_printer_id = (
                self.printing_product_label_printer_id
            )
        return res
