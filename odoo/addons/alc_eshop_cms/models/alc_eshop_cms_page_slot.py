# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AlcEshopCmsPageSlot(models.Model):
    _name = "alc.eshop.cms.page.slot"
    _description = "Page Slot"

    name = fields.Char(required=True)
