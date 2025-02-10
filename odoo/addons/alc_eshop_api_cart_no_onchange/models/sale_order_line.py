# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.model
    def _play_onchanges_cart_line(self, vals):
        # Disable onchange on sale order line
        # WE DO NOT WANT to call onchange on sale order line
        # when we update the cart. All the fields to update/create
        # are managed by compute methods if needed. Onchange methods
        # are only there for the user interface and are time consuming
        # Moreover, the play_onchanges method from the onchange_helper
        # force the recompute of all the fields for every field updated
        # to detect the fields changed by the onchange. A test into the
        # testsuite ensures that only well known onchange methods exist
        # into the code so we can safely disable this method
        return {}
