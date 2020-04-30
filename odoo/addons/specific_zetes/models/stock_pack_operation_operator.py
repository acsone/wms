# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class StockPackOperationSqlView(models.Model):

    _name = 'stock.pack.operation.operator'
    _auto = False

    write_date = fields.Datetime(readonly=True)
    qty_done = fields.Float(readonly=True)
    picking_destination_location_id = fields.Many2one(
        'stock.location', related='picking_id.location_dest_id', readonly=True
    )
    picking_id = fields.Many2one('stock.picking', readonly=True)
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
