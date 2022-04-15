# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

# pylint: disable=odoo-addons-relative-import
from odoo.addons.alc_eshop_form.hooks import _load_form_name_translations

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Load EShop Form Translations")
    if not version:
        return
    _load_form_name_translations(cr)
