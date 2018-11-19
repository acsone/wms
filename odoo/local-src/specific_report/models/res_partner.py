from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_hide_prices_deliveryslip = fields.Boolean('Hide prices on deliveryslip')
