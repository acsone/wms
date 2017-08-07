# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        self._assign_delivery_round()
        return result

    @api.one
    def _assign_delivery_round(self):
        """ When the sale order is confirmed,
        - if there is a shipping method (carrier) that map to a delivery
          template, then we try to find a matching instance
        - or if there is an existing instance matching the shipping address we
          insert the associate the new pickings/shipping to that round instance
        In all cases, a picking is associated to an round instance only if
        (partially) available
        """
        _logger.debug("Searching a delivery round for SO %d" % self.id)
        template = self.carrier_id.delivery_template_id
        # 1 shipping is created
        # multiple pickings could be created, or inserted in existing pickings

        pickings = self.picking_ids.filtered(
            lambda picking:
            picking.picking_type_subcode == 'PICK' and
            picking.state in ('confirmed',
                              'partially_available', 'assigned') and
            not picking.printed)
        if not pickings:
            return

        if template:
            _logger.debug("Associate SO %d to delivery instance matching "
                          "carrier" % self.id)
            delivery_round = self.env['round.instance'].search(
                [
                    ('template_id', '=', template.id),
                    ('state', '!=', 'done')
                ],
                order='date asc, time_leave_planned asc',
                limit=1,
            )
            if (delivery_round and pickings.mapped('delivery_round_id') and
                    delivery_round != pickings.mapped('delivery_round_id')):
                raise ValidationError(_(
                    "All pickings at destination of a same shipping must "
                    "be in the same delivery round"))
        else:
            delivery_round = pickings.mapped('delivery_round_id')
            if len(delivery_round) > 1:
                raise ValidationError(_(
                    "All pickings at destination of a same shipping must "
                    "be in the same delivery round"))
            if not delivery_round:
                delivery_round = self.env['round.instance'].find(
                    pickings[0].partner_id)

        if delivery_round:
            delivery_round._assign_pickings(pickings)
        _logger.debug("Searching a delivery round for SO %d. Done." % self.id)
