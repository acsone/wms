# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class CreditCommunication(models.TransientModel):

    _inherit = "credit.control.communication"

    payment_not_reconciled = fields.Many2many(
        'account.move.line', string='Un reconciled payment'
    )

    @api.model
    @api.returns('credit.control.line')
    def _get_credit_lines(self, line_ids, partner_id, level_id, currency_id):
        """Sort the lines to print on invoice date."""
        cr_lines = super(CreditCommunication, self)._get_credit_lines(
            line_ids, partner_id, level_id, currency_id
        )
        cr_lines.sorted(key=lambda r: r.date_sent)
        return cr_lines

    @api.model
    def _generate_comm_from_credit_lines(self, lines):
        comms = super(
            CreditCommunication, self
        )._generate_comm_from_credit_lines(lines)
        comms._get_payment()
        return comms

    @api.multi
    def _get_payment(self):
        """Get not reconciled payment for the client of the control line."""
        for comm in self:
            comm.payment_not_reconciled = (
                self.env['account.move.line']
                .search(
                    [
                        ('partner_id', '=', comm.partner_id.id),
                        ('reconciled', '=', False),
                        ('credit', '>', 0),
                        ('account_id.internal_type', 'in', ['receivable']),
                        (
                            'id',
                            'not in',
                            self.mapped(
                                'credit_control_line_ids.move_line_id'
                            ).ids,
                        ),
                        (
                            'company_id',
                            'in',
                            self.mapped(
                                'credit_control_line_ids.company_id'
                            ).ids,
                        ),
                    ]
                )
                .filtered(lambda l: l.move_id.state == 'posted')
            )

    @api.model
    def _get_total(self):
        total = super(CreditCommunication, self)._get_total()
        total += sum(self.mapped('payment_not_reconciled.balance'))
        return total

    @api.model
    def _get_total_due(self):
        total = super(CreditCommunication, self)._get_total_due()
        total += sum(self.mapped('payment_not_reconciled.amount_residual'))
        return total

    def get_consolidate_lines(self):
        """Unify data from credit_control_line_ids and payment_not_reconciled
        to print them all together in chronological order
        """
        self.ensure_one()
        lines = []
        for aml in self.payment_not_reconciled:
            lines.append(
                {
                    'invoice_id': aml.invoice_id,
                    'move_line_id': aml,
                    'date_entry': aml.date,
                    'date_due': aml.date_maturity,
                    'amount_due': aml.balance,
                    'balance_due': (aml.amount_residual or aml.balance),
                    'amount_currency_id': self.currency_id,
                    'balance_currency_id': self.currency_id,
                }
            )
            if aml.invoice_id:
                lines[-1]['name'] = aml.invoice_id.number
            else:
                lines[-1]['name'] = aml.name_get()[0][1]

        for aml in self.credit_control_line_ids:
            lines.append(
                {
                    'invoice_id': aml.invoice_id,
                    'move_line_id': aml.move_line_id,
                    'date_entry': aml.date_entry,
                    'date_due': aml.date_due,
                    'amount_due': aml.amount_due,
                    'balance_due': aml.balance_due,
                    'amount_currency_id': self.currency_id,
                    'balance_currency_id': aml.currency_id
                    or aml.company_id.currency_id,
                }
            )
            if aml.invoice_id:
                lines[-1]['name'] = aml.invoice_id.number
            else:
                lines[-1]['name'] = aml.move_line_id.name_get()[0][1]

        return sorted(
            lines, key=lambda r: fields.Date.from_string(r['date_entry'])
        )
