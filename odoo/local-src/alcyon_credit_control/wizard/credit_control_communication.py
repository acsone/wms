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
            comm.payment_not_reconciled = self.env['account.move.line'].search(
                [
                    ('partner_id', '=', comm.partner_id.id),
                    ('reconciled', '=', False),
                    ('account_id.internal_type', 'in', ['receivable', 'payable']),
                    ('id', 'not in', self.mapped('credit_control_line_ids.move_line_id').ids),
                    ('company_id', 'in', self.mapped('credit_control_line_ids.company_id').ids),
                ]
            ).filtered(lambda l: l.move_id.state == 'posted')

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
