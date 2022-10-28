# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo.addons.shopfloor_base.utils import _get_app_version


def _get_alc_version():
    module_name = "alc_all"
    regex = r"alc_shopfloor_version/alc_version.pyc?"
    module_path = re.sub(regex, module_name, __file__)
    return _get_app_version(module_name, module_path=module_path)
