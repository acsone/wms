# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.purchase.models.purchase import PurchaseOrder as PurchaseOrderBase


class PurchaseOrder(PurchaseOrderBase):
    nbr_lines = fields.Integer("Nbr lines", compute="_compute_nbr_lines")
    nbr_lines_bo = fields.Integer(
        "Nbr lines BO",
        compute="_compute_nbr_lines_bo",
        search="_search_nbr_lines_bo",
        readonly=True,
    )

    @api.depends("order_line")
    def _compute_nbr_lines(self):
        """
        Compute the number of lines by purchase order.

        :return:
        """
        for rec in self:
            rec.nbr_lines = len(rec.order_line)

    @api.depends("order_line")
    def _compute_nbr_lines_bo(self):
        """
        Compute the number of lines with back order by purchase order.

        :return:
        """
        for po in self:
            # NOTE: computing 'immediately_usable_qty' field is very slow,
            # especially when the field is displayed on PO tree view
            po.nbr_lines_bo = len(po.order_line.filtered("is_bo_line"))

    def _search_nbr_lines_bo(self, operator, value):
        orders = self.browse()
        draft_orders = self.search([("state", "=", "draft")])
        for order in draft_orders:
            # NOTE: actual operator is ignored here for the sake of simplicity.
            # To implement if it's really needed.
            if order.nbr_lines_bo:
                orders |= order
        return [("id", "in", orders.ids)]
