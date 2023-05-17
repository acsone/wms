# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import ValidationError


class MissingWeightError(ValidationError):
    def __init__(self):
        super().__init__(_("You must enter a weight for the product to receive"))


class MissingDimensionsError(ValidationError):
    def __init__(self):
        super().__init__(_("You must enter dimensions for the product to receive"))


class MissingBarcodeError(ValidationError):
    def __init__(self):
        super().__init__(
            _(
                "You must enter a barcode for the product to receive or allow the reception without barcode"
            )
        )
