from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    length = fields.Float('Length', help='Length')
    width = fields.Float('Width', help='Width')
    depth = fields.Float('Depth', help='Depth')

    @api.onchange('length', 'width', 'depth')
    def onchange_size(self):
        for product in self:
            volume = product.length * product.width * product.depth
            product.volume = volume

    @api.model
    def get_default_state_id(self):
        """
        I need to do this check because the "default" for the state_id
        can be call before data are loaded
        """
        state_active = \
            self.env.ref('specific_purchase.product_state_active', False)

        if state_active:
            return state_active.id

    date_out_of_stock_expected = fields.Datetime('Expected out of stock date')
    state_id = fields.Many2one(
        'product.state',
        string='State',
        default=get_default_state_id
    )


class ProductState(models.Model):
    _name = 'product.state'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()
