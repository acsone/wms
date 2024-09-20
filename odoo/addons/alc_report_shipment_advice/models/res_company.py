# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields

from odoo.addons.base.models.res_company import Company


class ResCompany(Company):

    # TODO: This should be removed when package category will be completely
    # migrated (data)
    shipment_advice_packages_display_mode = fields.Selection(
        [("source", "Per Source Zone"), ("package", "Per Package Category")],
        default="source",
    )
