# Copyright 2017 Camptocamp SA
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields
from odoo.fields import NewId

from odoo.addons.sale.models import sale_order_line


class SaleOrder(sale_order_line.SaleOrderLine):

    esb_ref = fields.Char(string="Reference for ESB", copy=False, index=True)
    newpharma_ref = fields.Integer(string="Reference for NewPharma", copy=False)

    initial_exception = fields.Char(
        help="keep track of the exception on the line. This field preserve the "
        "original exception even when ignore exception is set.",
    )

    def _ws_manage_newpharma_exceptions(self: NewId, partner_ref) -> bool:
        """
        This will detect if exception is present on sale order line,.

        if the partner is NewPharam, set the ordered quantity to 0.

        self is a NewId as a prepared recordset to be created.

        Returns boolean if an exception is present
        """
        if self.main_exception_id:
            initial_exception = self.main_exception_id.description
            # FIXME: add boolean on res_partner to filter web service users
            vals = {
                "ignore_exception": True,
                "initial_exception": initial_exception,
            }
            if partner_ref in self.env["res.partner"].newpharma_refs:
                vals["product_uom_qty"] = 0
            self.update(vals)
            return True
        return False
