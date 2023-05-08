# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner as PartnerBase


class ResPartner(PartnerBase):
    auto_cancel_unavailable_qty_sold = fields.Boolean(
        string="Auto-cancel Unavailable Quantity",
        default=False,
        help=(
            "Automatically cancel unavailable ordered quantity to avoid the "
            "generation of backorders.\n"
            "In other words it will ship only immediately usable quantity."
        ),
    )
