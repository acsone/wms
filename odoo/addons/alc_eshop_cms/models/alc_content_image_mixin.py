# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from . import AlcCmsMixin


class AlcContentImageMixin(AlcCmsMixin):

    _name = "alc.content.image.mixin"
    _description = "Alc Content Image Mixin"

    content = fields.Html(required=True, translate=True, sanitize=False)
