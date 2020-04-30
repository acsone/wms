# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    esb_ref = fields.Integer(string='Reference for ESB', copy=False)
