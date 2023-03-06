# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.purchase.models import purchase


class PurchaseOrder(purchase.PurchaseOrder):

    prepayment = fields.Boolean(
        "Prepayment",
        help="Check this if the invoice is received before reception of goods",
    )
