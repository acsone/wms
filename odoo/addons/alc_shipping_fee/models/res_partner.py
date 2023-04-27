# © 2017 Julien Coux (Camptocamp)
# © 2018 Yannick Vaucher (Camptocamp)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):

    help_with_fee = fields.Boolean(string="Helps with fees")
    help_with_fixed_fee = fields.Boolean(
        string="Fixed fee applied for deliveries",
        help="If checked, a fixed amount for delivery will be apply, "
        "no matter the amount of the delivery",
    )
