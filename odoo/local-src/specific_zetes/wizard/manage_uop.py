import logging

from odoo import fields, models, _
from odoo.exceptions import UserError

from .. import constants

_logger = logging.getLogger(__name__)


class ManageUOP(models.TransientModel):
    _name = 'manage.uop'

    user_id = fields.Many2one('res.users', string='User')
    uop = fields.Integer('UOP')
    picking_id = fields.Many2one('stock.picking', string='UOP')
    line_ids = fields.One2many('manage.uop.line', 'wizard_id', string='Lines')
    is_change_lots = fields.Boolean('Change lots')
    printer_num = fields.Integer(string='Printer', default=1, required=True)
    nbr_package = fields.Integer('Nbr package', default=1, required=True)
    state = fields.Selection([('main_menu', 'Main Menu'),
                              ('search_picking', 'Search Picking'),
                              ('validate_picking', 'Validate Picking')],
                             default='main_menu')

    def search_picking(self):
        self.ensure_one()

        if self.uop:
            pickings = \
                self.env['stock.picking'].search([('id', '=', self.uop)])
            if not pickings:
                raise UserError(_('UOP not found'))
        elif self.user_id:
            pickings = self.env['stock.picking'].search([
                ('operator_id', '=', self.user_id.id),
                ('state', 'in', ('partially_available', 'assigned')),
                ('picking_type_subcode', '=', 'PICK')
            ])
        else:
            raise UserError(_('Please insert the UOP or the user'))

        if not pickings:
            raise UserError(_('You do not have an UOP'))

        if len(pickings) == 1:
            self.picking_id = pickings.id
            self.load_picking()
        else:
            self.state = 'search_picking'

        return self.reload_page()

    def load_picking(self):
        self.state = 'validate_picking'

        if not self.picking_id:
            raise UserError(_('Please select an UOP'))

        line_to_update = self.picking_id.pack_operation_ids.filtered(
                lambda line: line.zetes_state == constants.OP_MISSING)

        self.is_change_lots = len(line_to_update)
        for pack_op in line_to_update:
            self.line_ids.create({
                'wizard_id': self.id,
                'pack_op_id': pack_op.id,
                'qty': pack_op.product_qty
            })

        return self.reload_page()

    def validate(self):
        self.ensure_one()

        for line in self.line_ids:
            if not line.lot_id:
                raise UserError(_('Please set a lot'))
            line.pack_op_id.add_qty(line.qty, lot_id=line.lot_id.id)

        if not self.printer_num:
            raise UserError(_('Please select the printer'))

        printer_toshiba = self.env['printing.printer'].search(
            [('code', '=', self.printer_num), ('type', '=', 'toshiba')])
        printer_zebra = self.env['printing.printer'].search(
            [('code', '=', self.printer_num), ('type', '=', 'zebra')])

        if not printer_toshiba or not printer_zebra:
            raise UserError(_('Printer not found'))

        # Put in pack
        try:
            # Create a pack for this picking
            box = self.picking_id.put_in_pack()
            if box:
                # Set the number of packages for this picking
                box.nbr_packages = self.nbr_package
        except Exception as e:
            _logger.error(e)
            self.print_passport()
            raise UserError(_('Cannot create the package. '
                              'Please give the passport to your manager'))

        # Print labels
        try:
            self.picking_id.print_products_label(printer=printer_toshiba)
            self.picking_id.print_packages_label(printer=printer_zebra)
        except Exception as e:
            _logger.error(e)
            self.print_passport()
            raise UserError(_('Cannot print labels. '
                              'Please give the passport to your manager'))

        # Validate the picking
        try:
            self.picking_id.do_new_transfer()
        except Exception as e:
            _logger.error(e)
            self.print_passport()
            raise UserError(_('Cannot validate the UOP. '
                              'Please give the passport to your manager'))

        wizard = self.create({})
        wizard.reload_page()

    def reload_page(self):
        action = self.env.ref('specific_zetes.manage_uop_action').read([])[0]
        action.update({
            'res_id': self.id
        })
        return action

    def print_passport(self):
        pick_aliment = \
                self.env.ref('__setup__.stock_picking_type_ali')
        pick_frigo = \
            self.env.ref('__setup__.stock_picking_type_froid')

        if self.picking_id.picking_type_id == pick_aliment:
            printer_code = constants.PRINTER_ALIMENT
        elif self.picking_id.picking_type_id == pick_frigo:
            printer_code = constants.PRINTER_FRIGO
        else:
            printer_code = constants.PRINTER_MEDICAMENT

        printer = self.env['printing.printer'].search(
            [('code', '=', printer_code), ('type', '=', 'pdf')])

        self.picking_id.print_passport_report(printer=printer)


class ManageLotLine(models.TransientModel):
    _name = 'manage.uop.line'

    wizard_id = fields.Many2one('change.lot', string='Wizard')
    product_id = fields.Many2one(
        'product.product', string='Product',
        related='pack_op_id.product_id', readonly=True)
    pack_op_id = fields.Many2one('stock.pack.operation', 'Line', required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    qty = fields.Integer('Qty', required=True)
