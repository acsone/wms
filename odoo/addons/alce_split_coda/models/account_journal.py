# Copyright 2018 Okia SPRL (sylvain@okia.be)
# Copyright 2023 ACSONE SA/NV
import base64
import re

from odoo.addons.l10n_be_coda.models.account_journal import AccountJournal as Journal


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
        pattern = re.compile("[\u0020-\u1EFF\n\r]+")  # printable characters
        final_attachment_ids = set()
        # This in order to return super() with account.journal model instead of
        # recordset to avoid constraints triggered in _find_additional_data()
        codas_in_attachments = False
        for attachment in attachments:
            for encoding in (
                "utf_8",
                "cp850",
                "cp858",
                "cp1140",
                "cp1252",
                "iso8859_15",
                "utf_32",
                "utf_16",
                "windows-1252",
            ):
                try:
                    record_data = attachment.raw.decode(encoding)
                except UnicodeDecodeError:
                    continue
                if pattern.fullmatch(record_data, re.MULTILINE):
                    break
            if self._check_coda(record_data):
                i = 1
                for coda in self._split_codas(record_data):
                    # Naïve name (don't take into account possible file extension)
                    coda_part_name = "-".join([attachment.name, str(i)])
                    final_attachment_ids.add(
                        self.env["ir.attachment"]
                        .create(
                            {
                                "name": coda_part_name,
                                "datas": base64.b64encode(coda),
                            }
                        )
                        .id
                    )
                    i += 1
                if i > 1:
                    # Only set this if there are several statements in coda
                    codas_in_attachments = True
            else:
                # Simply add the current attachement to those that will be returned
                # to super()
                final_attachment_ids.add(attachment.id)
        if codas_in_attachments:
            new_self = self.env["account.journal"].browse()
        else:
            new_self = self
        return super(AccountJournal, new_self)._import_bank_statement(
            self.env["ir.attachment"].browse(final_attachment_ids)
        )

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

            current_coda += line + "\n"

            # Code 9 => the end of the statement
            if line[0] == "9":
                yield current_coda.encode("utf-8")
