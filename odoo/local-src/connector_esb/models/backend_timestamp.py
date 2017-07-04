# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ESBBackendTimestamp(models.Model):
    _name = 'esb.backend.timestamp'
    _description = 'Keep time of last export'

    backend_id = fields.Many2one(
        comodel_name='esb.backend',
        string='Backend Id',
        required=True,
    )
    model = fields.Char(
        string='Model name',
        required=True
    )
    kind = fields.Char(
        string='Kind of export'
    )
    last_export = fields.Datetime(
        string='Timestamp last export'
    )
