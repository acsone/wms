# Copyright 2017 Camptocamp SA
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields

from odoo.addons.sale.models import sale_order_line


class SaleOrder(sale_order_line.SaleOrderLine):

    esb_ref = fields.Char(string="Reference for ESB", copy=False, index=True)
    newpharma_ref = fields.Integer(string="Reference for NewPharma", copy=False)

    initial_exception = fields.Char(
        help="keep track of the exception on the line. This field preserve the "
        "original exception even when ignore exception is set.",
    )
