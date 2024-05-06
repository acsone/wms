# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):

    invoice_amount_copy = fields.Integer(
        "Amount of invoice copies to generate",
        help="If amount = 1, then 2 invoices will be generated in the pdf "
        "(original + copy)",
    )
