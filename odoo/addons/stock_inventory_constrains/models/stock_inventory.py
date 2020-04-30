# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    @api.constrains('location_id', 'filter')
    def _check_all_product_on_main_location(self):
        for inventory in self:
            if inventory.filter != 'none':
                continue
            if (
                inventory.location_id
                and inventory.location_id.is_inventory_forbidden
            ):
                raise ValidationError(
                    _(
                        "You cannot create an inventory for 'all products' on the %s location."
                    )
                    % inventory.location_id.name
                )
