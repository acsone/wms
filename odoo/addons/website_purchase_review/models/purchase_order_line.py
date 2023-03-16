# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields

from odoo.addons.purchase.models.purchase import (
    PurchaseOrderLine as PurchaseOrderLineBase,
)


class PurchaseOrderLine(PurchaseOrderLineBase):

    is_confirmed_line = fields.Boolean("Confirmed line")
