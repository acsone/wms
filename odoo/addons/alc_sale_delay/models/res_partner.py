# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models import res_partner


class ResPartner(res_partner.Partner):

    max_delay_for_sale_order_creation = fields.Float(
        string="Max delay on sale order creation",
        digits=(3, 4),
        help="Used to compute if the processing of a sale order in"
        "the background takes too long. (0.5 is 30 minutes)",
    )
