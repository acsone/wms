# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.queue_job.job import job


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _get_cart_to_recompute_price_domain(self):
        """ Return a domain used to get the cart to recompute prices.
        """
        return [
            ("typology", "=", "cart"),
            ("date_order", "<", fields.Date.today()),
        ]

    @api.model
    def _cron_recompute_cart_price(self):
        carts = self.search(self._get_cart_to_recompute_price_domain())
        for cart in carts:
            description = _("Recalculate prices on cart %s") % cart.name
            cart.with_delay(description=description)._recalculate_cart_price_to_now()

    @job(default_channel="root.background.process")
    def _recalculate_cart_price_to_now(self):
        """ Recompute prices on cart.
        """
        self.write({"date_order": fields.Datetime.now()})
        for cart in self:
            cart.recalculate_prices()
        return True
