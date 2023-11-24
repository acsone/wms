# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models import res_partner


class ResPartner(res_partner.Partner):

    email_invoice = fields.Char(
        "Invoice Email",
        help="If set, this address will be used for invoice mailing",
    )
