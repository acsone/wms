# -*- coding: utf-8 -*-
# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    storage_type_new = env.ref("alc_stock_storage_type.package_st_M_M_Nouveaute")
    storage_type_new.is_new = True
