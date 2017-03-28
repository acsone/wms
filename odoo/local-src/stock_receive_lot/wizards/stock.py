# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields
from openerp.exceptions import Warning


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'
    _rec_name = 'product_id'

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s (%d/%d)' % (
                rec.product_id.display_name,
                rec.qty_done, rec.product_qty,
                )))
        return result


class StockPackOperationLotAdd(models.TransientModel):
    _name = 'stock.pack.operation.lot.add'

    name = fields.Char(default='New')

    picking_id = fields.Many2one(
        'stock.picking', readonly="True")
    partner_id = fields.Many2one(
        related='picking_id.partner_id', readonly=True)
    origin = fields.Char(
        related='picking_id.origin', readonly=True)

    operation_id = fields.Many2one(
        'stock.pack.operation',
        string="Operation",
        domain=[('state', '=', 'assigned')])

    def _is_parent_child(self, parent, child):
        if child.parent_left and child.parent_right:
            if parent.parent_left > child.parent_left:
                return False
            if parent.parent_right < child.parent_right:
                return False
            return True
        else:
            # parent_left/right could be deferred and it is disabled in init
            # mode during unittesting
            while child.location_id:
                if child.location_id == parent:
                    return True
                child = child.location_id
            return False

    @api.onchange('operation_id')
    def _onchange_operation_id(self):
        if not (self.location_dest_id and
                self._is_parent_child(self.location_op_dest_id,
                                      self.location_dest_id)):
            # If in the wizard, there is no location or if the current location
            # is not valid for selected operation then we need to update it
            if self.operation_id.location_dest_id.usage == 'internal':
                self.location_dest_id = self.operation_id.location_dest_id
            else:
                self.location_dest_id = False
        if not self.lot_required:
            self.life_date = False
            self.lot_name = False

    location_op_dest_id = fields.Many2one(
        'stock.location', 'Operation Destination View Location',
        compute='_get_location_op_dest_id')

    @api.one
    @api.depends('operation_id')
    def _get_location_op_dest_id(self):
        loc = self.operation_id.location_dest_id
        while loc and loc.usage != 'view':
            loc = loc.location_id
        self.location_op_dest_id = loc.id

    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location', required=True)

    lot_required = fields.Boolean('Lot Required', compute='_get_lot_required')

    @api.depends('operation_id')
    @api.one
    def _get_lot_required(self):
        self.lot_required = self.operation_id.product_id.tracking != 'none'

    product_qty = fields.Float(
        related='operation_id.product_qty',
        readonly=True)
    product_uom_id = fields.Many2one(
        'product.uom',
        related='operation_id.product_uom_id',
        readonly=True)
    remaining_qty = fields.Float(
        'Qty Remaining',
        compute='_get_remaining_qty')

    @api.depends('operation_id')
    @api.one
    def _get_remaining_qty(self):
        self.remaining_qty = (
            self.operation_id.product_qty - self.operation_id.qty_done)

    qty = fields.Float('Qty Done')

    life_date = fields.Datetime(
        string='End of Life Date')

    @api.onchange('life_date')
    def _onchange_life_date(self):
        oplot = self.env['stock.pack.operation.lot']
        if self.life_date:
            self.lot_name = oplot._calc_lotname_from_lifedate(self.life_date)

    is_removal_date_expired = fields.Boolean(
        'Removal Date Expired',
        compute='_get_is_removal_date_expired')

    @api.depends('life_date')
    def _get_is_removal_date_expired(self):
        oplot = self.env['stock.pack.operation.lot']
        line = oplot.new({
            'life_date': self.life_date,
            'operation_id': self.operation_id.id})
        self.is_removal_date_expired = line.is_removal_date_expired

    lot_name = fields.Char('Lot Name')
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot')

    def _convert_lot_name2id(self, vals):
        operation = (
            self.operation_id or
            self.env['stock.pack.operation'].browse(vals['operation_id']))
        lot_obj = self.env['stock.production.lot']
        lot = lot_obj.search([
            ('name', '=', vals['lot_name']),
            ('product_id', '=', operation.product_id.id)])
        if not lot:
            lot = lot_obj.create({
                'name': vals['lot_name'],
                'product_id': operation.product_id.id})
        vals['lot_id'] = lot.id

    @api.model
    def create(self, vals):
        if vals.get('lot_name'):
            self._convert_lot_name2id(vals)
        wiz = super(StockPackOperationLotAdd, self).create(vals)
        if vals.get('life_date'):
            wiz.lot_id.life_date = vals['life_date']
            wiz.lot_id.onchange_life_date()
        return wiz

    @api.multi
    def write(self, vals):
        if vals.get('lot_name'):
            self._convert_lot_name2id(vals)
        res = super(StockPackOperationLotAdd, self).write(vals)
        for rec in self:
            if (rec.lot_id and rec.life_date and
                    rec.lot_id.life_date != rec.life_date):
                rec.lot_id.life_date = rec.life_date
                rec.lot_id.onchange_life_date()
        return res

    def _add(self):
        if self.qty <= 0:
            raise Warning('Quantity must be greater than 0')

        # A pack operation is for a destination and can have multiple lot lines
        # (pack_lot_ids) with the constraint that you cannot have 2 lot lines
        # with the same name (then we need to increase qty of existing line)
        # So while the destination stay the same, we can fill lines, otherwise
        # we need to split the pack operation and adjust the processed and
        # remaining quantities
        if self.location_dest_id != self.operation_id.location_dest_id:
            if self.operation_id.pack_lot_ids:
                # Location changed - split pack
                pack = self.operation_id
                pack2 = pack.copy(default={
                    'qty_done': 0.0,
                    'product_qty': pack.product_qty - pack.qty_done,
                    })
                pack.product_qty = pack.qty_done
                pack._copy_remaining_pack_lot_ids(pack2.id)
                self.operation_id = pack2
            self.operation_id.location_dest_id = self.location_dest_id

        lot_name = self.lot_id.name
        if lot_name:
            for lot in self.operation_id.pack_lot_ids:
                if lot.lot_name == lot_name:
                    lot.qty += self.qty
                    break
            else:
                self.operation_id.pack_lot_ids = [(0, 0, {
                    'qty': self.qty,
                    'lot_name': self.lot_id.name,
                    })]
        self.operation_id.save()

    @api.multi
    def button_nextop(self):
        self.button_nextlot()
        self.operation_id = False

    @api.multi
    def button_nextlot(self):
        self._add()
        self.qty = False
        self.lot_id = False  # ensure we don't modify lot on next lines
        self.life_date = False
        self.lot_name = False

    @api.multi
    def button_nextdestloc(self):
        self._add()
        self.qty = False
        self.location_dest_id = False
