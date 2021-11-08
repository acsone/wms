# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError


class MissingWeightError(UserError):
    def __init__(self):
        super(MissingWeightError, self).__init__(
            _("You must enter a weight for the product to receive")
        )


class MissingDimensionsError(UserError):
    def __init__(self):
        super(MissingDimensionsError, self).__init__(
            _("You must enter dimensions for the product to receive")
        )


class MissingBarcodeError(UserError):
    def __init__(self):
        super(MissingBarcodeError, self).__init__(
            _(
                "You must enter a barcode for the product to receive or allow the reception without barcode"
            )
        )
