from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_discount = fields.Float('Supplier discount %')
    is_back_order_accepted = fields.Boolean('Back order accepted')
