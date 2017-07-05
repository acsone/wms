from odoo import fields, models, api


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'
    _order = 'location_name'

    location_name = fields.Char('Location name',
                                related='location_id.name',
                                store=True)
