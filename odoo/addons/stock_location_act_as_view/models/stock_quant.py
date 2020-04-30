# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_move(
        self,
        quants,
        move,
        location_to,
        location_from=False,
        lot_id=False,
        owner_id=False,
        src_package_id=False,
        dest_package_id=False,
        entire_pack=False,
    ):
        if location_to.act_as_view:
            raise exceptions.UserError(
                _('You cannot move to a location acting as view %s.')
                % (location_to.name,)
            )
        return super(StockQuant, self).quants_move(
            quants,
            move,
            location_to,
            location_from=location_from,
            lot_id=lot_id,
            owner_id=owner_id,
            src_package_id=src_package_id,
            dest_package_id=dest_package_id,
            entire_pack=entire_pack,
        )
