# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_company import Company


class ResCompany(Company):

    restrict_move_line_quantity = fields.Boolean(
        help="Check this box if you want to restrict a zero or a negative quantity in a stock move line (reserved_uom_qty)"
    )
