# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
import json
import logging
import re
from functools import reduce

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

SALT = '"zeGE"'


def textToChars(text):
    return map(ord, list(text))


def applySaltToChar(salt, code):
    return reduce(lambda a, b: a ^ b, textToChars(salt), code)


def decipher(salt):
    """decrypt token from QRCode printed on the employee badge and
    encoded using the methods proposed here:
    https://stackoverflow.com/questions/18279141/javascript-string-encryption-and-decryption
    """

    def decode(encoded):
        encoded = encoded.replace(" ", "")
        regex = r".{1,2}"
        vals = re.findall(regex, encoded)
        vals = map(lambda s: int(s, 16), vals)
        vals = map(lambda s: applySaltToChar(salt, s), vals)
        vals = map(unichr, vals)
        return "".join(vals)

    return decode


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "barcodes.barcode_events_mixin"]

    def on_barcode_scanned(self, barcode):
        """ Try to assign the operator if not yet assigned and barcode is
        an operator
        """
        if not self.operator_id:
            try:
                payload = decipher(SALT)(barcode)
                login = json.loads(payload)["login"]
                user = self.env["res.users"].search([("login", "=", login)])
                if user:
                    self.operator_id = user
                    return None
            except Exception:
                _logger.exception(
                    "Unable to decode user barcode or wrong user barcode %s", barcode
                )
            raise UserError(
                _("Please scan your user badge first to start the operations")
            )

        return super(StockPicking, self).on_barcode_scanned(barcode)
