# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import config


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    only_tax_ids = fields.Many2many('account.tax',
                                    compute='_compute_all_taxes')
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


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'report.async']

    @api.multi
    def get_report_name(self):
        """Generate a specific name for the report save in ir.attachment"""
        self.ensure_one()
        if self.state == 'draft':
            # Not saving in ir.attachment when in draft state
            return None
        if not self.partner_id.ref:
            raise UserError(_(
                'The Quotation can not be printed the client {} ({}) \
                 has no reference assigned.')
                .format(self.partner_id.name, self.partner_id.id)
            )
        return '_'.join([
            'cf',
            self.partner_id.ref,
            str(self.id),
            ''.join(self.create_date[:10].split('-')),
            ''.join(self.create_date[-8:].split(':')),
            ]) + '.pdf'

    @api.multi
    def action_confirm(self):
        """ Generate the sale order pdf and save it in ir.attachment"""
        res = super(SaleOrder, self).action_confirm()
        if (config['test_enable'] or
                self.env.context.get('skip_pdf_gen')):
            # Do not generate the report during test or during import
            return res
        for order in self:
            self.with_delay().print_and_attach_report(
                'sale.report_saleorder',
                order.partner_id.fax if order.sale_channel == 'fax' else None
            )
        return res

    @api.multi
    def print_quotation(self):
        """Only keep one sale order with the same name in ir.attachment"""
        res = super(SaleOrder, self).print_quotation()
        for so in self:
            filename = so.get_report_name()
            existing = self.env['ir.attachment'].search([
                ('name', '=', filename),
                ('res_model', '=', 'sale.order')])
            existing.unlink()
        return res
