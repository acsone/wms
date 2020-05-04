# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # unset operator_id initialized with the default user id
    cr.execute("update stock_scrap set operator_id = null;")
