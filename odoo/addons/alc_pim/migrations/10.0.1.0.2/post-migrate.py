# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

# pylint: disable=odoo-addons-relative-import
from odoo.addons.alc_pim.hooks import _load_attribute_options_translations

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Load PIM Options Translations")
    openupgrade.load_data(cr, "alc_pim", "data/attribute_option.xml", mode="init")
    if not version:
        return
    _load_attribute_options_translations(cr)
