# -*- coding: utf-8 -*-
# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ModifySerialNumber(models.TransientModel):
    _name = "modify.serial.number"

    serial_number = fields.Char(required=True)

    @api.model
    def default_get(self, fields):
        result = super(ModifySerialNumber, self).default_get(fields)

        if self._context.get("active_id"):
            move = self.env["stock.move"].browse(self._context["active_id"])
            result["serial_number"] = move.serial_number

        return result

    @api.multi
    def save_new_serial_number(self):
        self.ensure_one()

        if not self._context.get("active_id"):
            raise UserError(_("No active id found"))

        stock_move = self.env["stock.move"].browse(self._context["active_id"])
        stock_move.write({"serial_number": self.serial_number})
        stock_move.move_dest_id.write({"serial_number": self.serial_number})
