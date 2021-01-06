# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, models
from odoo.exceptions import UserError


class product_price_list(models.TransientModel):
    _inherit = "product.price_list"

    @api.multi
    def print_report(self):
        """
        To get the date and print the report
        @return : return report
        """
        current_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model")

        if active_model == "product.template":
            ids = (
                self.env["product.template"]
                .browse(current_ids)
                .mapped("product_variant_ids")
                .ids
            )
        elif active_model == "product.product":
            ids = current_ids
        else:
            raise UserError(
                _("Unable to print pricelist for product with current model %s")
                % active_model
            )
        return super(
            product_price_list, self.with_context(active_ids=ids)
        ).print_report()
