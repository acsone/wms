# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models import res_partner


class ResPartner(res_partner.Partner):
    opt_out = fields.Boolean(
        "Opt-Out",
        help="If opt-out is checked, this contact has refused to receive emails for mass mailing and marketing campaign. "
        "Filter 'Available for Mass Mailing' allows users to filter the partners when performing mass mailing.",
        default=True,
    )
