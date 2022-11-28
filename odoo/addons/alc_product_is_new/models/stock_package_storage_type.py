# -*- coding: utf-8 -*-
# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackageStorageType(models.Model):
    _inherit = "stock.package.storage.type"

    is_new = fields.Boolean(default=False)
