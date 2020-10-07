# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_packagings(self, move):
        # return biggest package first ...
        return move.product_id.mapped("packaging_ids").sorted("qty", reverse=True)

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
                "Reserve by packaging. Current domain: %s. " "Preferred domain: %s",
                domain,
                preferred_domain_list,
            )
            config_param = self.env["ir.config_parameter"]
            min_qty = float(
                config_param.get_param("stock.reservation_unit_min_quantity", 0)
            )
            preferred_domain_list = []
            exclude_domain = []
            if qty >= min_qty:
                for packaging in self._get_packagings(move):
                    factor = packaging.packaging_type_id.stock_reservation_factor
                    if not factor:
                        continue
                    min_reservable_qty = packaging.qty * factor
                    if min_reservable_qty and qty >= min_reservable_qty:
                        preferred_domain_list.append(
                            [("qty", ">=", min_reservable_qty)] + exclude_domain
                        )
                        exclude_domain.append(("qty", "<", min_reservable_qty))

                if preferred_domain_list:
                    preferred_domain_list.append(exclude_domain)
            _logger.debug(
                "Reserve by packaging. New preferred domain: %s", preferred_domain_list
            )
        return super(StockQuant, self).quants_get_preferred_domain(
            qty,
            move,
            ops=ops,
            lot_id=lot_id,
            domain=domain,
            preferred_domain_list=preferred_domain_list,
        )
