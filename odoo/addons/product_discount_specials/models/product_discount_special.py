# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from dateutil.relativedelta import relativedelta

from odoo import fields, models


def default_today(recordset):
    return recordset._context.get("date", fields.Date.context_today(recordset))


def default_in_one_month(recordset):
    today_str = default_today(recordset)
    today = fields.Date.from_string(today_str)
    return fields.Date.to_string(today + relativedelta(months=1))


class ProductDiscountSpecial(models.Model):
    _name = "product.discount.special"

    sequence = fields.Integer("Sequence")

    date_start = fields.Date("Start Date", required=True, default=default_today)
    date_end = fields.Date("End Date", required=True, default=default_in_one_month)

    product_template_id = fields.Many2one("product.template", required=True)
