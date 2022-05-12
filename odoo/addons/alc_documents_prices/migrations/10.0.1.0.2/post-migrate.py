# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    query = "UPDATE alc_document SET document_date = NULL WHERE compute in ('pricelist', 'discount');"
    cr.execute(query)
