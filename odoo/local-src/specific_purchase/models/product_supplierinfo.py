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

        if self.name and self.product_tmpl_id:
            self._onchange_update_price_and_ref()

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.name and self.product_tmpl_id:
            self._onchange_update_price_and_ref()

    def _onchange_update_price_and_ref(self):
        # TODO Use base purchase price instead of sale
        self.price = self.product_tmpl_id.list_price

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
