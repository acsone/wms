from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    nbr_packages = fields.Integer('Number of packages', default=1)
    original_picking_zone_id = fields.Many2one(
        'picking.zone', 'Original picking zone'
    )
