from odoo import fields, models, api


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'
    _order = 'location_name'

    location_name = fields.Char('Location name',
                                compute='_compute_location_name',
                                store=True)

    @api.multi
    @api.depends('location_id.name')
    def _compute_location_name(self):
        for operation in self:
            operation.location_name = operation.location_id.name
