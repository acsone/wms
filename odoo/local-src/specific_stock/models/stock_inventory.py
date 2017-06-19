# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    INVENTORY_NAMES = ['expensive', 'best_sellers', 'other']

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
    def create_daily_inventory(self, date_today_overwrite=None):
        """
        Create the daily inventory.
        This method is call by the cron.
        We need to create an inventory only for open days
        (and ignore bank holidays).
        :return:
        """
        # I'll no use fields.Date.today because I want to have the object
        date_today = date_today_overwrite or date.today()

        # If the current day is Saturday or Sunday we skip the inventory
        if date_today.isoweekday() in [6, 7]:
            return

        # If the current day is a bank holiday we skip the inventory
        bank_holiday = self.env['bank.holiday'].search([
            ('date', '=', fields.Date.to_string(date_today))
        ])
        if bank_holiday:
            return

        inventory = self.create({
            'name': _('Daily inventory: %s') % fields.Date.today(),
            'filter': 'partial',
        })
        product_obj = self.env['product.product']
        inventory_periods = self.compute_inventory_periods(
            date_today_overwrite=date_today_overwrite
        )
        products_inventory = product_obj.get_products_daily_inventory(
            inventory_periods, date_today_overwrite=date_today_overwrite
        )

        if not products_inventory:
            inventory.unlink()
            return

        location = self.env.ref('stock.stock_location_stock').location_id
        for product in products_inventory:
            inventory.line_ids.create({
                'inventory_id': inventory.id,
                'product_id': product.id,
                'location_id': location.id,
            })

        return inventory

    @api.model
    def compute_inventory_periods(self, date_today_overwrite=None):
        config_param = self.env['ir.config_parameter']

        date_now = date_today_overwrite or date.today()
        fiscal_year = \
            self.env.user.company_id.compute_fiscalyear_dates(date_now)
        fiscal_year_from = fiscal_year['date_from']

        periods = {}
        for inventory in self.INVENTORY_NAMES:
            delay = int(config_param.get_param(
                'stock.delay_inventory_%s_products' % inventory
            ))
            if not delay:
                raise UserError(
                    _('There is no delay for the inventory %s' % inventory)
                )

            date_start_period = fiscal_year_from
            date_end_period = \
                date_start_period + \
                relativedelta(months=delay) - \
                relativedelta(days=1)
            while date_end_period < date_now:
                date_start_period = date_end_period + relativedelta(days=1)
                date_end_period = \
                    date_start_period + \
                    relativedelta(months=delay) - \
                    relativedelta(days=1)

            periods[inventory] = {
                'date_start': fields.Date.to_string(date_start_period),
                'date_end': fields.Date.to_string(date_end_period),
                'delay': delay,
                'nbr_inventory_per_year': 12 / delay,
            }

        return periods


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
