# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools

from .. import constants


class StockPackOperationSqlView(models.Model):

    _name = 'stock.pack.operation.operator'
    _auto = False

    location_processed = fields.Boolean(readonly=True)
    additional_move_id = fields.Many2one('stock.move', readonly=True)
    qty_backorder = fields.Integer(readonly=True)
    location_name = fields.Char(readonly=True)
    location_dest_name = fields.Char(readonly=True)
    create_date = fields.Date(readonly=True)
    picking_id = fields.Many2one('stock.picking', readonly=True)
    product_id = fields.Many2one('product.product', readonly=True)
    product_uom_id = fields.Many2one('product.uom', readonly=True)
    product_qty = fields.Float(readonly=True)
    ordered_qty = fields.Float(readonly=True)
    qty_done = fields.Float(readonly=True)
    qty_done_uom_ordered = fields.Float(readonly=True)
    is_done = fields.Boolean(readonly=True)
    package_id = fields.Many2one('stock.quant.package', readonly=True)
    pack_lot_ids = fields.One2many('stock.pack.operation.lot', readonly=True)
    result_package_id = fields.Many2one('stock.quant.package', readonly=True)
    date = fields.Datetime(readonly=True)
    owner_id = fields.Many2one('res.partner', readonly=True)
    linked_move_operation_ids = fields.One2many(
        'stock.move.operation.link', readonly=True
    )
    remaining_qty = fields.Float(readonly=True)
    location_id = fields.Many2one('stock.location', readonly=True)
    location_dest_id = fields.Many2one('stock.location', readonly=True)
    picking_source_location_id = fields.Many2one(
        'stock.location', related='picking_id.location_id', readonly=True
    )
    picking_destination_location_id = fields.Many2one(
        'stock.location', related='picking_id.location_dest_id', readonly=True
    )
    from_loc = fields.Char(readonly=True)
    to_loc = fields.Char(readonly=True)
    fresh_record = fields.Boolean(readonly=True)
    lots_visible = fields.Boolean(readonly=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('waiting', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('partially_available', 'Partially Available'),
            ('assigned', 'Available'),
            ('done', 'Done'),
        ],
        related='picking_id.state',
        readonly=True,
    )
    zetes_state = fields.Selection(
        [
            (constants.OP_DEFAULT, 'Default'),
            (constants.OP_PICKED, 'Picked'),
            (constants.OP_SHORTPICKED, 'Shortpicked'),
            (constants.OP_SKIPPED, 'Skipped'),
            (constants.OP_CUT, 'Cut'),
            (constants.OP_CANCELED, 'Canceled / Full'),
            (constants.OP_MISSING, 'Missing'),
        ],
        readonly=True,
    )

    operator_id = fields.Many2one('res.users', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
              SELECT
                  spo.*,
                  sp.operator_id as operator_id
              FROM
                  stock_pack_operation as spo
              JOIN
                  stock_picking as sp
                  ON sp.id = spo.picking_id
        """
        self.env.cr.execute(
            "CREATE OR REPLACE VIEW " + self._table + " AS (" + query + ")"
        )
