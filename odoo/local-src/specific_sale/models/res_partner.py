# -*- coding: utf-8 -*-
# © 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def action_view_sales_available(self):
        self.ensure_one()
        action = self.env.ref(
            'specific_sale.action_product_sale_available_list'
        )

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': [
                ('state', 'in', ['sale', 'done']),
                ('order_id.partner_id', '=', self.id)
            ],
        }
