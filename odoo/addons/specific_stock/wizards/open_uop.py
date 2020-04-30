# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class OpenUOP(models.TransientModel):
    _name = 'open.uop'

    uop = fields.Integer('UOP', required=True)

    def open_uop(self):
        """
        We use the ID (called UOP) of the picking for Zetes to increase
        the speed of transaction.
        If a picker has a problem with a picking, he need to have a
        quickly access to his picking. A picker shouldn't not see the standard
        view of Odoo.
        It is why I offer a wizard to open a picking by his UOP
        :return:
        """
        self.ensure_one()

        picking = self.env['stock.picking'].search([('id', '=', self.uop)])
        if not picking:
            raise UserError(_('This UOP does\'t exist'))

        return {
            'name': 'UOP',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'view_id': self.env.ref('stock.view_picking_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.uop,
            'context': self._context,
            'target': 'current',
        }
