# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase


class SaleOrderLine(SaleOrderLineBase):

    b2c_ref = fields.Char(string="Reference B2C", copy=False)

    _sql_constraints = [  # the ref should be unique per order only
        (
            "b2c_ref_unique",
            "EXCLUDE (b2c_ref WITH =, order_id WITH =) WHERE (b2c_ref <> '' or b2c_ref is not null)",
            _("This b2c reference already exists"),
        )
    ]
