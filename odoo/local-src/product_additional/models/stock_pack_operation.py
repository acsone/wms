from odoo import fields, models


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    is_additional_line = fields.Boolean('Is additional line')
