# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs


def migrate(cr, version):
    query_get = """SELECT id, name, audience FROM alc_eshop_form"""
    cr.execute(query_get)
    rs = cr.fetchall()
    id_codes = [(r[0], "_".join((r[1][:3].upper(), r[2][:3].upper()))) for r in rs]
    values = ["({}, '{}')".format(rid, code) for rid, code in id_codes]

    query_create = "ALTER TABLE alc_eshop_form ADD COLUMN code VARCHAR;"
    cr.execute(query_create)

    query_set = """
UPDATE alc_eshop_form
SET code = new_value.code
FROM (VALUES %s) new_value (id, code)
WHERE new_value.id = alc_eshop_form.id"""
    cr.execute(query_set, (AsIs(", ".join(values)),))
