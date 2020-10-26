# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    @api.multi
    def _compute_available_quantities_dict(self):
        """change the way immediately_useable_qty is computed by:
        * deducing the quants in excluded locations
        * adding the quantities of moves with a lower priority or same
          priority but later date
        """
        res, stock_dict = super(
            ProductProduct, self
        )._compute_available_quantities_dict()
        prio = self.env.context.get("prio")
        date = self.env.context.get("date")
        corrections = {}
        exclude_location_ids = (
            self.env["stock.location"].get_excluded_from_immediately_usable_qty().ids
        )

        if exclude_location_ids:
            excluded_qty_dict = self.with_context(
                location=exclude_location_ids
            )._compute_quantities_dict(
                self._context.get("lot_id"),
                self._context.get("owner_id"),
                self._context.get("package_id"),
                self._context.get("from_date"),
                self._context.get("to_date"),
            )

        if prio is not None and date is not None:
            (
                dom_quant_loc,
                dom_move_in_loc,
                dom_move_out_loc,
            ) = self._get_domain_locations()
            domain = dom_move_out_loc + [
                # We never want to overwrite a move,
                # which ends in the loss location. The quantity isn't usable
                # and would have to be deducted in the end anyway.
                ("product_id", "in", self.ids),
                ("state", "not in", ("done", "cancel")),
                "|",
                ("priority", "<", prio),
                "&",
                ("priority", "=", prio),
                ("date", ">", date),
            ]
            move_groupby = self.env["stock.move"].read_group(
                domain, ["product_id", "product_qty"], ["product_id"], orderby="id"
            )
            for group in move_groupby:
                corrections[group["product_id"][0]] = group["product_qty"]

        for product_id in res:
            deducted_amounts = 0.0
            if exclude_location_ids:
                deducted_amounts += excluded_qty_dict[product_id]["incoming_qty"]
                deducted_amounts += excluded_qty_dict[product_id]["qty_available"]

            res[product_id]["immediately_usable_qty"] += (
                corrections.get(product_id, 0) - deducted_amounts
            )
        return res, stock_dict
