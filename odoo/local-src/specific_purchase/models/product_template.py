from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    date_out_of_stock_expected = fields.Datetime('Expected out of stock date')
    state_id = fields.Many2one(
        'product.state',
        string='State',
        default=lambda x: x.env.ref(
            'specific_purchase.product_state_active').id)


class ProductState(models.Model):
    _name = 'product.state'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()
