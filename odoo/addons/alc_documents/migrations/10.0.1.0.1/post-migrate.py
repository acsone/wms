# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    query = "UPDATE alc_document SET type = 'order' WHERE name like 'cf_%';"
    cr.execute(query)
    query = "UPDATE alc_document SET type = 'delivery_note' WHERE name like 'NE_%';"
    cr.execute(query)
    query = "UPDATE alc_document SET type = 'invoice' WHERE name like 'fc_%';"
    cr.execute(query)
    query = "UPDATE alc_document SET type = 'credit_note' WHERE name like 'nc_%';"
    cr.execute(query)
