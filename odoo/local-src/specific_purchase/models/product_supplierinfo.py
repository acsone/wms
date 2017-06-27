from odoo import models, api


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    @api.onchange('name')
    def onchange_name(self):
        if not self.name or not self.name.delivery_lead_time:
            return

        delay = self.name.delivery_lead_time
        self.delay = delay
