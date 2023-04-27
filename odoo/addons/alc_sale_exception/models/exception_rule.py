# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.sale_exception.models import exception_rule


class ExceptionRule(exception_rule.ExceptionRule):

    warning_text = fields.Char(
        help="Text which appears in sale order lines if the exception is non blocking"
    )
