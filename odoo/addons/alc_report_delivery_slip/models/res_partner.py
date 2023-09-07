# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.delivery.models.partner import ResPartner as Partner


class ResPartner(Partner):

    is_hide_prices_deliveryslip = fields.Boolean("Hide prices on deliveryslip")
    show_deliveryslip_cnk = fields.Boolean("Show CNK on delivery slip")
    is_hide_entry_register = fields.Boolean(
        string="Hide entry register on delivery slip"
    )
