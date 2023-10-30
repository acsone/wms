# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import ValidationError


class NoBackOrderError(ValidationError):
    def __init__(self, product_name, order_ref):
        error_msg = _(
            "No back order quantity for product %(name)s in sale order %(order_ref)s",
            name=product_name,
            order_ref=order_ref,
        )
        super().__init__(error_msg)
