from odoo import models, api, fields, _


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

    @api.multi
    def open_form_view(self):
        self.ensure_one()
        view = self.env.ref('specific_purchase.product_supplierinfo_view_form')

        return {
            'name': _('Supplier info'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
            'context': self.env.context
        }
