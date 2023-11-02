# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.account_invoice_supplier_ref_unique.models.res_company import (
    ResCompany as ResCompanyBase,
)


class ResCompany(ResCompanyBase):

    _inherit = "res.company"

    check_invoice_supplier_number_mandatory = fields.Boolean(
        help="Check this if you want a mandatory Invoice Supplier Number",
    )
