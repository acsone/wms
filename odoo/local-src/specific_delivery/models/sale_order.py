    # -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import defaultdict

from openerp import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    only_tax_ids = fields.Many2many('account.tax', compute='_compute_all_taxes')
    contribution_ids = fields.Many2many('account.tax',
                                        compute='_compute_all_taxes')
    apb_ids = fields.Many2many('account.tax', compute='_compute_all_taxes')
    amount_contribution = fields.Monetary(compute='_compute_all_taxes')

    @api.multi
    @api.depends('tax_id')
    def _compute_all_taxes(self):
        tax_group_apb = self.env.ref('specific_account.tax_group_apb')

        for line in self:
            amount_contribution = 0
            only_tax_ids = self.env['account.tax']
            contribution_ids = self.env['account.tax']
            apb_ids = self.env['account.tax']

            for tax in line.tax_id:
                if tax.include_base_amount:
                    amount_contribution += (tax.amount * line.qty_delivered)
                    contribution_ids |= tax
                elif tax.tax_group_id == tax_group_apb:
                    apb_ids |= tax
                else:
                    only_tax_ids |= tax

            line.only_tax_ids = only_tax_ids
            line.contribution_ids = contribution_ids
            line.apb_ids = apb_ids
            line.amount_contribution = amount_contribution
