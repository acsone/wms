# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.osv import expression

from odoo.addons.stock.models import product


class ProductProduct(product.Product):
    def _get_domain_locations(self):
        (
            domain_quant_loc,
            domain_move_in_loc,
            domain_move_out_loc,
        ) = super()._get_domain_locations()
        if self._excludes_expired_lot_from_qty_available():
            domain_quant_loc = expression.AND(
                [
                    domain_quant_loc,
                    self._get_domain_quant_lots(),
                ]
            )
        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc

    @api.model
    def _excludes_expired_lot_from_qty_available(self):
        return bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "alc_stock_available_product_expiry.excludes_expired_lot_from_qty_available"
            )
        )

    def _get_domain_quant_lots(self):
        max_expiration_date = fields.Datetime.now()
        from_date = self.env.context.get("from_date", False)
        if from_date:
            max_expiration_date = from_date
        to_date = self.env.context.get("to_date", False)
        if to_date:
            max_expiration_date = to_date

        removal_op = ">"
        compute_expired_only = self.env.context.get("compute_expired_only")
        if compute_expired_only:
            removal_op = "<="

        lot_domain = expression.AND(
            [[("lot_id", "!=", False)], [("lot_id.expiration_date", "!=", False)]]
        )

        quants_lot_domain = expression.AND(
            [
                lot_domain,
                [("lot_id.expiration_date", removal_op, max_expiration_date)],
            ]
        )
        if not compute_expired_only:
            removal_unset_domain = expression.OR(
                [[("lot_id", "=", False)], [("lot_id.expiration_date", "=", False)]]
            )
            quants_lot_domain = expression.OR(
                [
                    removal_unset_domain,
                    quants_lot_domain,
                ]
            )
        return quants_lot_domain
