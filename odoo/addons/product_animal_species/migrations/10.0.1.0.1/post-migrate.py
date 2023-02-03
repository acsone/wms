# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

# pylint: disable=odoo-addons-relative-import
from odoo.addons.product_animal_species.hooks import _load_species_translations

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Load Animal Species Translations")
    if not version:
        return
    _load_species_translations(cr)
