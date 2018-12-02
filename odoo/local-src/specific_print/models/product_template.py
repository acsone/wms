from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_do_not_print_label = fields.Boolean('Do not print label')
