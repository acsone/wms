# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval



class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_put_in_pack_done = fields.Boolean("Put in Pack done", default=False)

    @api.multi
    def name_get(self):
        """ Display the name, the partner and the round """
        res = []
        for picking in self:
            name = picking.name
            if picking.partner_id:
                name += u" - %s" % picking.partner_id.display_name
            if picking.delivery_round_id:
                name += u" - %s" % picking.delivery_round_id.template_code
            res.append((picking.id, name))
        return res

    @api.multi
    def _create_lots_for_picking(self):
        return super(
            StockPicking, self.with_context(default_life_date_allowed=True)
        )._create_lots_for_picking()
