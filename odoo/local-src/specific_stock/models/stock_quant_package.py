from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    nbr_packages = fields.Integer('Number of packages', default=1)
    original_picking_type_id = fields.Many2one('stock.picking.type',
                                               'Original picking type')
