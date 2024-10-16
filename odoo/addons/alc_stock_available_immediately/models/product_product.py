# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock_available_immediately_exclude_location.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
    _inherit = "product.product"

    def _compute_available_quantities_dict(self):
        """
        Change the way immediately_usable_qty is computed by adding the quantities.

        of moves with a lower priority or same priority but later date
        """
        res, stock_dict = super()._compute_available_quantities_dict()
        prio = self.env.context.get("prio")
        date = self.env.context.get("date")
        corrections = {}

        if prio is not None and date is not None:
            (
                _dom_quant_loc,
                _dom_move_in_loc,
                dom_move_out_loc,
            ) = self._get_domain_locations()
            domain = [
                *dom_move_out_loc,
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
            res[product_id]["immediately_usable_qty"] += corrections.get(product_id, 0)
        return res, stock_dict
