# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    order_phone = fields.Char(string="Order phone")
    order_fax = fields.Char(string="Order fax")

    invoice_terms_conditions = fields.Text(
        string="Invoice Terms and Conditions", translate=True
    )
    delivery_terms_conditions = fields.Html(
        string="Delivery Terms and Conditions", translate=True
    )
