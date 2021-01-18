# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class AlcAccountPaymentGlobalization(models.TransientModel):

    _name = "alc.account.payment.globalization"

    partner_id = fields.Many2one(
        "res.partner", string="Globalization counter party", required=True
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        default=lambda a: a._get_default_journal_id(),
    )

    date = fields.Date(
        string="Posting date", required=True, default=fields.Date.context_today
    )

    payment_mode_id = fields.Many2one(
        "account.payment.mode", string="Payment mode", required=True
    )
    account_id = fields.Many2one(
        "account.account",
        string="Account",
        required=True,
        default=lambda a: a._get_default_account_id(),
    )

    @api.model
    def _get_default_journal_id(self):
        return self.env["account.journal"].search([("code", "=", "ODDOM")], limit=1).id

    @api.model
    def _get_default_account_id(self):
        return self.env["account.account"].search([("code", "=", "400000")]).id

    def _get_globalizable_lines(self):
        self.ensure_one()
        return self.env["account.move.line"].search(
            [
                ("payment_mode_id", "=", self.payment_mode_id.id),
                ("reconciled", "=", False),
                ("account_id", "=", self.account_id.id),
            ]
        )

    def _prepare_line_values(self, move_line):
        self.ensure_one()
        amount_residual = move_line.amount_residual
        vals = {
            "invoice_id": move_line.invoice_id.id,
            "name": u"{} {}".format(move_line.invoice_id.number, self.partner_id.name),
            "account_id": self.account_id.id,
            "partner_id": move_line.partner_id.id,
        }
        if amount_residual > 0:
            vals["credit"] = amount_residual
        else:
            vals["debit"] = -amount_residual
        return vals

    def _prepare_values(self, move_lines):
        line_ids = []
        values = {
            "date": self.date,
            "journal_id": self.journal_id.id,
            "line_ids": line_ids,
        }
        globalization_amount = 0.0
        # credit all the vet
        for move_line in move_lines:
            line_values = self._prepare_line_values(move_line)
            globalization_amount += line_values.get("credit", 0)
            globalization_amount -= line_values.get("debit", 0)
            line_ids.append((0, 0, line_values))

        # debit chronovet
        date_localized = self.env["ir.qweb.field.date"].value_to_html(self.date, {})
        globalization_line_vals = {
            "name": u"Prélèvement {}".format(date_localized),
            "account_id": self.account_id.id,
            "partner_id": self.partner_id.id,
            "payment_mode_id": self.partner_id.customer_payment_mode_id.id,
            "mandate_id": self.partner_id.valid_mandate_id.id,
        }
        if globalization_amount > 0:
            globalization_line_vals["debit"] = globalization_amount
        else:
            globalization_line_vals["credit"] = -globalization_amount
        line_ids.append((0, 0, globalization_line_vals))
        return values

    def _reconcile(self, move_lines, new_move_lines):
        AccountMoveLine = self.env["account.move.line"]
        move_line_id_by_invoice = defaultdict(list)
        new_move_line_id_by_invoice = defaultdict(list)
        for line in move_lines:
            move_line_id_by_invoice[line.invoice_id].append(line.id)
        for line in new_move_lines:
            new_move_line_id_by_invoice[line.invoice_id].append(line.id)
        for invoice, line_ids in move_line_id_by_invoice.items():
            line_ids.extend(new_move_line_id_by_invoice[invoice])
            AccountMoveLine.browse(line_ids).reconcile()

    def _after_globalization(self, account_move):
        pass

    @api.multi
    def doit(self):
        self.ensure_one()
        move_lines = self._get_globalizable_lines()
        move_vals = self._prepare_values(move_lines)
        # create account move
        account_move = self.env["account.move"].create(move_vals)
        # reconcile invoice with credit lines
        self._reconcile(move_lines, account_move.line_ids)
        self._after_globalization(account_move)
        return account_move.get_formview_action()
