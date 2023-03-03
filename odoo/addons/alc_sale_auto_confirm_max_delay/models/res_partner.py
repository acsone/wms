# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models.res_partner import ResPartner as ResPartnerBase


class ResPartner(ResPartnerBase):

    auto_confirm_max_delay = fields.Float(
        string="Max delay on sale order operation",
        digits=(3, 4),
        help="Max delay between the order creation and the auto confirmation by the "
        "system. This value applies to orders created by the api.",
    )
