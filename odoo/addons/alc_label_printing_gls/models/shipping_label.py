# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.job import job


class ShippingLabel(models.Model):

    _inherit = "shipping.label"

    @api.model
    def create(self, vals):
        res = super(ShippingLabel, self).create(vals)
        if res.package_id.carrier_id.delivery_type == "gls":
            description = _(u"Printing label {}").format(self.name)
            res.with_delay(description=description, priority=10).hw_print()
        return res

    @job
    def hw_print(self, printer=False):
        printer = printer or self.env.user.printing_printer_id
        if isinstance(printer, int):
            printer = self.env["printing.printer"].browse(printer)
        if not printer:
            raise ValidationError(_("No printer assigned."))
        for label in self:
            content = base64.decodebytes(label.datas)
            printer.print_document(None, content, "pdf")
