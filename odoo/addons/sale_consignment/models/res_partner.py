# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_stock_consignment_customer = fields.Many2one(
        'stock.location',
        string="Customer Consignment Location",
        company_dependent=True,
        help="This stock location will be used for consignment orders "
        "as the destination location for goods you send to this partner",
    )
