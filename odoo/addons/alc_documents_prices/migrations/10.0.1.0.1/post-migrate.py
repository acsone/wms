# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    query = "UPDATE alc_document SET type = 'pricelist' WHERE compute = 'pricelist';"
    cr.execute(query)
    query = "UPDATE alc_document SET type = 'discount' WHERE compute = 'discount';"
    cr.execute(query)
