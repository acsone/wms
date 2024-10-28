# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields

from odoo.addons.account.models import account_analytic_line
from odoo.addons.sale.models.sale_order_line import SaleOrderLine


class AccountMoveLine(account_analytic_line.AccountAnalyticLine):

    so_line = fields.Many2one[SaleOrderLine](index=True)
