# Copyright 2018 Okia SPRL (sylvain@okia.be)
# Copyright 2023 ACSONE SA/NV

from io import BytesIO

from odoo.addons.l10n_be_coda.models.account_journal import AccountJournal as Journal


class CodaStatement:
    """
    Simple object to simulate the raw property of an attachment that.

    super()._parse_bank_statement_file is waiting for
    """

    raw = BytesIO


class AccountJournal(Journal):
    def _import_bank_statement(self, attachments):
        """
        Split and import a coda by statement.

        The bank ING send a CODA file with several account numbers.
        However Odoo can only manage one account number per CODA.

        To import this kind of CODA we need to split the CODA file
        and import statement by statement.
        Moreover the bank can send several bank statement in the same file.
        """
        for attachment in attachments:
            data = attachment.raw
            if not self._check_coda(data):
                return super()._import_bank_statement(attachment)
            # Split the coda file by statement and pass it to the parser
            res = None
            for coda in self._split_codas(data):
                res = super()._parse_bank_statement_file(coda)
            return res

    def _split_codas(self, data):
        """
        Split the CODA file by statements.

        A CODA file is a formatted file
        who contains a list of statements grouped by account number.

        In a CODA file, each line starts with a code (a number).
        Each grouped statements starts with the code 0 and ends with the
        code 9. Thus if we want to split a CODA file, we simply need
        to cut each blocks starting with 0 and ending with 9.
        :param data:
        :return: object containing statement as BytesIO: CodaStatement
        """
        recordlist = data.split("\n")

        current_coda = ""
        for line in recordlist:
            if not line:
                continue

            # Code 0 => the beginning of the statement
            if line[0] == "0":
                current_coda = ""

            current_coda += line

            # Code 9 => the end of the statement
            if line[0] == "9":
                statement = CodaStatement()
                statement.raw = current_coda.encode()
                yield statement
