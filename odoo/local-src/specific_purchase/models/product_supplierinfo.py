from odoo import models, api, fields


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    product_cnk_code = fields.Char(related='product_tmpl_id.cnk_code',
                                   readonly=True)

    @api.onchange('name')
    def onchange_name(self):
        if not self.name.delivery_lead_time:
            return

        delay = self.name.delivery_lead_time
        self.delay = delay
