# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, models
from odoo.addons.queue_job.job import job


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    @job(default_channel='root.db2.create_or_update')
    def _regroup_shipping_bo(self):
        """ Regroup shippings backorders by partners

        Search for first existing BO shipping
        and assign all other BO shipping to it

        """
        loc_customers = self.env.ref('stock.stock_location_customers')
        ship_backorders = self.env['stock.picking'].search(
            [('partner_id', '=', self.id),
             ('state', '=', 'waiting'),
             ('location_dest_id', '=', loc_customers.id)],
            )
        if len(ship_backorders) > 1:
            target = ship_backorders[0]
            to_del = ship_backorders[1:]
            to_del.mapped('move_lines').write({'picking_id': target.id})
            to_del.unlink()
