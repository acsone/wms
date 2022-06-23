# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    @api.model
    def _index(self, bin_data, datas_fname, file_type):
        return False
