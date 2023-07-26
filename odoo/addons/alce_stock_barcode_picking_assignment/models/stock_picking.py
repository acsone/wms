# Copyright 2021 ACSONE SA/NV
import json
import logging
import re
from functools import reduce

from odoo import _
from odoo.exceptions import UserError
from odoo.tools import config

from odoo.addons.alce_stock_barcode_easy_operation.models import stock_picking

_logger = logging.getLogger(__name__)

SALT = '"zeGE"'


def textToChars(text):
    return map(ord, list(text))


def applySaltToChar(salt, code):
    return reduce(lambda a, b: a ^ b, textToChars(salt), code)


def decipher(salt):
    """Decrypt token from QRCode printed on the employee badge and.

    encoded using the methods proposed here:
    https://stackoverflow.com/questions/18279141/javascript-string-encryption-and-decryption
    """

    def decode(encoded):
        encoded = encoded.replace(" ", "")
        regex = r".{1,2}"
        vals = re.findall(regex, encoded)
        vals = (int(s, 16) for s in vals)
        vals = (applySaltToChar(salt, s) for s in vals)
        vals = map(chr, vals)
        return "".join(vals)

    return decode


class StockPicking(stock_picking.StockPicking):
    def on_barcode_scanned(self, barcode):
        """Try to assign the operator if not yet assigned and barcode is.

        an operator. Once operator is assigned, printed is set to True
        """
        if self.action_start_allowed and not config["test_enable"]:
            try:
                payload = decipher(SALT)(barcode)
                login = json.loads(payload)["login"]
                user = self.env["res.users"].search([("login", "=", login)])
                if user:
                    self.action_start()
                    self.user_id = user
                    return None
            except Exception:  # pylint: disable=broad-except'
                _logger.exception(
                    "Unable to decode user barcode or wrong user barcode %s", barcode
                )
            raise UserError(
                _("Please scan your user badge first to start the operations")
            )
        return super().on_barcode_scanned(barcode)
