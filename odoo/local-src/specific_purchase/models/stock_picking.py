from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        self.ensure_one()

        result = super(StockPicking, self).do_new_transfer()

        if not result or result['res_model'] != 'stock.backorder.confirmation':
            return result

        wiz_id = result['res_id']
        wiz = self.env['stock.backorder.confirmation'].browse(wiz_id)

        if self.partner_id.is_back_order_accepted:
            result = wiz.process()
        else:
            result = wiz.process_cancel_backorder()

        return result
