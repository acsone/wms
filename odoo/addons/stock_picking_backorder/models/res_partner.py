# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_sale_back_order_accepted = fields.Boolean(
        string="Sale backorder accepted",
        default=True,
        track_visibility="onchange",
        help="Do not let customer order products not in stock",
    )
    is_sale_back_order_cancel = fields.Boolean(
        string="Sale backorder auto-cancel",
        track_visibility="onchange",
        help=(
            "Automaticaly cancel products that could not be delivered. "
            "Must be set on delivery addresss"
        ),
    )
    is_purchase_back_order_accepted = fields.Boolean(
        string="Purchase backorder accepted"
    )
