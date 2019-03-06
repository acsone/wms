# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_get_preferred_domain(
        self,
        qty,
        move,
        ops=False,
        lot_id=False,
        domain=None,
        preferred_domain_list=None,
    ):
        if not preferred_domain_list and not lot_id:
            _logger.debug(
                "Reserve by packaging. Current domain: %s. "
                "Preferred domain: %s",
                domain,
                preferred_domain_list,
            )
            config_param = self.env['ir.config_parameter']
            min_qty = float(
                config_param.get_param(
                    'stock.reservation_unit_min_quantity', 0
                )
            )
            preferred_domain_list = []
            exclude_domain = []
            if qty >= min_qty:
                pallet_factor = float(
                    config_param.get_param(
                        'stock.reservation_unit_pallet_factor', 1
                    )
                )
                pallet_qty = move.product_id.unit_in_pallet * pallet_factor
                if pallet_qty and qty > pallet_qty:
                    preferred_domain_list.append(
                        [('qty', '>=', pallet_qty)] + exclude_domain
                    )
                    exclude_domain.append(('qty', '<', pallet_qty))

                box_factor = float(
                    config_param.get_param(
                        'stock.reservation_unit_box_factor', 1
                    )
                )
                box_qty = move.product_id.unit_in_box * box_factor
                if box_qty and qty > box_qty:
                    preferred_domain_list.append(
                        [('qty', '>=', box_qty)] + exclude_domain
                    )
                    exclude_domain.append(('qty', '<', box_qty))

                wrap_factor = float(
                    config_param.get_param(
                        'stock.reservation_unit_wrap_factor', 1
                    )
                )
                wrap_qty = move.product_id.unit_in_shrink_wrap * wrap_factor
                if wrap_qty and qty > wrap_qty:
                    preferred_domain_list.append(
                        [('qty', '>=', wrap_qty)] + exclude_domain
                    )
                    exclude_domain.append(('qty', '<', wrap_qty))

                if preferred_domain_list:
                    preferred_domain_list.append(exclude_domain)
            _logger.debug(
                "Reserve by packaging. New preferred domain: %s",
                preferred_domain_list,
            )
        return super(StockQuant, self).quants_get_preferred_domain(
            qty,
            move,
            ops=ops,
            lot_id=lot_id,
            domain=domain,
            preferred_domain_list=preferred_domain_list,
        )
