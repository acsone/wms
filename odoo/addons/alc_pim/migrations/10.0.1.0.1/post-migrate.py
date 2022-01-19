# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

# pylint: disable=odoo-addons-relative-import
from odoo.addons.alc_pim.hooks import _load_attribute_options_translations

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Load PIM Options Translations")
    if not version:
        return
    _load_attribute_options_translations(cr)
