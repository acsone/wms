from odoo import fields, models, _

from odoo.exceptions import UserError

from .. import constants


class ChangeLot(models.TransientModel):
    _name = 'change.lot'

    uop = fields.Integer('UOP', required=True)
    line_ids = fields.One2many('change.lot.line', 'wizard_id', string='Lines')
    state = fields.Selection([('new', 'New'), ('get', 'Get')], default='new')

    def load_uop(self):
        self.ensure_one()

        picking = self.env['stock.picking'].search([('id', '=', self.uop)])

        if not picking:
            raise UserError(_('Invalid UOP'))

        pack_ops = picking.pack_operation_ids.filtered(
            lambda line: line.zetes_state == constants.OP_MISSING)

        for pack_op in pack_ops:
            self.line_ids.create({
                'wizard_id': self.id,
                'pack_op_id': pack_op.id,
                'qty': pack_op.product_qty
            })

        self.state = 'get'

        action = self.env.ref('specific_zetes.change_lot_action').read([])[0]
        action.update({
            'res_id': self.id
        })
        return action

    def validate(self):
        self.ensure_one()

        for line in self.line_ids:
            if not line.lot_id:
                raise UserError(_('Please set a lot'))
            pack_lots = line.pack_op_id.pack_lot_ids
            pack_lots.create({
                'operation_id': line.pack_op_id.id,
                'qty': line.qty,
                'lot_id': line.lot_id.id,
            })

            line.pack_op_id.qty_done += line.qty


class ChangeLotLine(models.TransientModel):
    _name = 'change.lot.line'

    wizard_id = fields.Many2one('change.lot', string='Wizard')
    product_id = fields.Many2one(
        'product.product', string='Product',
        related='pack_op_id.product_id', readonly=True)
    pack_op_id = fields.Many2one('stock.pack.operation', 'Line', required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    qty = fields.Integer('Qty', required=True)
