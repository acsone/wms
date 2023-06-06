# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api
from odoo.exceptions import ValidationError

from odoo.addons.delivery_carrier_label_gls.models.shipping_label import (
    ShippingLabel as Label,
)


class ShippingLabel(Label):
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if rec.package_id.carrier_id.delivery_type == "gls":
                description = _("Printing label %(name)s", name=rec.name)
                rec.with_delay(description=description, priority=4).hw_print()
        return res

    def hw_print(self, printer=False):
        printer = printer or self.env.user.printing_gls_printer_id
        if isinstance(printer, int):
            printer = self.env["printing.printer"].browse(printer)
        if not printer:
            raise ValidationError(_("No GLS printer assigned."))
        for label in self:
            content = base64.b64decode(label.datas)
            printer.print_document(None, content)
