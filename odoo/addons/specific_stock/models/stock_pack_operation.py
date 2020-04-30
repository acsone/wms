from odoo import fields, models


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'
    _order = 'location_name'

    location_name = fields.Char(
        'Location name', related='location_id.name', store=True, readonly=True
    )
    operator_id = fields.Many2one(
        'res.users', related='picking_id.operator_id', readonly=True
    )
    location_dest_name = fields.Char(
        'Location dest name',
        related='location_dest_id.name',
        store=True,
        readonly=True,
    )
