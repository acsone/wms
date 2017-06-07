# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from odoo import fields, models, api, _


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def action_done(self):
        result = super(StockInventory, self).action_done()

        if self.env.context.get('qty_updated'):
            return result

        products = self.line_ids.mapped('product_id')
        products.write({
            'date_last_inventory': fields.Datetime.now()
        })

        return result

    @api.model
    def create_daily_inventory(self):
        """
        Create the daily inventory.
        This method is call by the cron.
        We need to create an inventory only for open days
        (and ignore bank holidays).
        :return:
        """
        # I'll no use fields.Date.today because I want to have the object
        date_today = date.today()

        # If the current day is Saturday or Sunday we skip the inventory
        if date_today.isoweekday() in [6, 7]:
            return

        # TODO check bank holidays with the issue ALCN-838

        inventory = self.create({
            'name': _('Daily inventory: %s') % fields.Date.today(),
            'filter': 'partial',
        })
        product_obj = self.env['product.product']
        products_inventory = product_obj.get_products_daily_inventory()

        if not products_inventory:
            inventory.unlink()
            return

        for product in products_inventory:
            inventory.line_ids.create({
                'inventory_id': inventory.id,
                'product_id': product.id,
            })


class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"

    @api.multi
    def change_product_qty(self):
        """
        When the user update the quantity on hand (with the wizard)
        we don't want to change the last inventory date
        :return:
        """
        return super(ProductChangeQuantity,
                     self.with_context(qty_updated=True)).change_product_qty()
