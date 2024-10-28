# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.search_engine_image_thumbnail.models import se_thumbnail


class SeThumbnail(se_thumbnail.SeThumbnail):

    base_name = fields.Char(index=True)
