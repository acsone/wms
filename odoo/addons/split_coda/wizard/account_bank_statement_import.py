# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL (sylvain@okia.be)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging

from odoo import _, api, models
from odoo.addons.base.res.res_bank import sanitize_account_number
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    @api.multi
    def import_file(self):
        """
        Split and import a coda by statement.

        The bank ING send a CODA file with several account numbers.
        However Odoo can only manage one account number per CODA.

        To import this kind of CODA we need to split the CODA file
        and import statement by statement.
        Moreover the bank can send several bank statement in the same file.
        It's why we need to check if the bank account is in Odoo.
        :return:
        """
        self.ensure_one()

        data = base64.b64decode(self.data_file)

        if not self._check_coda(data):
            return super(AccountBankStatementImport, self)._parse_file(data)

        # Split the code file
        codas = self.split_codas(data)

        statement_ids = []
        notifications = []
        for coda in codas:
            encoded_coda = "\n".join(coda).encode("windows-1252")
            currency_code, account_number, stmts_vals = self.with_context(
                active_id=self.ids[0]
            )._parse_file(encoded_coda)
            # Check raw data
            self._check_parsed_data(stmts_vals)

            sanitized_account_number = sanitize_account_number(account_number)

            # Check if the account number is valid
            journal_obj = self.env["account.journal"]
            journal = journal_obj.browse(self.env.context.get("journal_id", []))
            is_valid_account = self._check_journal_bank_account(
                journal, sanitized_account_number
            )
            if journal.bank_account_id and not is_valid_account:
                _logger.info("Skip the CODA for account %s" % account_number)
                continue

            # Try to find the currency and journal in odoo
            currency, journal = self._find_additional_data(
                currency_code, account_number
            )

            # If no journal found, ask the user about creating one
            if not journal:
                # The active_id is passed in context so the wizard can call
                # import_file again once the journal is created
                return self.with_context(
                    active_id=self.ids[0]
                )._journal_creation_wizard(currency, account_number)
            if (
                not journal.default_debit_account_id
                or not journal.default_credit_account_id
            ):
                raise UserError(
                    _(
                        "You have to set a Default Debit Account and a Default "
                        "Credit Account for the journal: %s"
                    )
                    % journal.name
                )
            # Prepare statement data to be used for bank statements creation
            stmts_vals = self._complete_stmts_vals(stmts_vals, journal, account_number)
            # Create the bank statements
            new_statement_ids, new_notifications = self._create_bank_statements(
                stmts_vals
            )
            statement_ids += new_statement_ids
            notifications += new_notifications

            # Now that the import worked out, set it as the
            # bank_statements_source of the journal
            journal.bank_statements_source = "file_import"

        if not statement_ids:
            raise UserError(_("No coda imported. Please check the journal"))

        # Finally dispatch to reconciliation interface
        action = self.env.ref("account.action_bank_reconcile_bank_statements")
        return {
            "name": action.name,
            "tag": action.tag,
            "context": {"statement_ids": statement_ids, "notifications": notifications},
            "type": "ir.actions.client",
        }

    @api.multi
    def split_codas(self, data):
        """
        Split the CODA file by statements. A CODA file is a formatted file
        who contains a list of statements grouped by account number.

        In a CODA file, each line starts with a code (a number).
        Each grouped statements starts with the code 0 and ends with the
        code 9. Thus if we want to split a CODA file, we simply need
        to cut each blocks starting with 0 and ending with 9.
        :param data:
        :return:
        """
        recordlist = unicode(data, "windows-1252", "strict").split("\n")

        splitted_codas = []
        current_coda = None
        for line in recordlist:
            if not line:
                continue

            # Code 0 => the beginning of the statement
            if line[0] == "0":
                current_coda = []

            current_coda.append(line)

            # Code 9 => the end of the statement
            if line[0] == "9":
                splitted_codas.append(current_coda)

        return splitted_codas
