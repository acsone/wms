# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):

    _inherit = 'res.partner'

    edi_backend_id = fields.Many2one(
        comodel_name="edi.backend", string="Edi connector"
    )
    use_edi_connector = fields.Boolean()

    @api.constrains("use_edi_connector", "edi_backend_id")
    def _check_edi_connector(self):
        for rec in self:
            if rec.use_edi_connector and not rec.edi_backend_id:
                raise ValidationError(_("An EDI connector is required."))

    def check_is_edi_supported(self):
        for record in self:
            if not record.use_edi_connector:
                raise UserError(_("EDI is not supported by %s") % record.name)
