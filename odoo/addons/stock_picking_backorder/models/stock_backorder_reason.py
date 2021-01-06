# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class StockBackorderReason(models.Model):
    _name = "stock.backorder.reason"
    _order = "name"

    name = fields.Char(string="Name", required=True, translate=True)
    backorder_action_to_do = fields.Selection(
        selection=[
            ("create", "Create backorder"),
            ("cancel", "Cancel backorder"),
            ("use_partner_option", "Use partner option (Purchase backorder accepted)"),
        ],
        string="Backorder action to do",
    )
    keep_grn = fields.Boolean("Keep GRN on backorder")
