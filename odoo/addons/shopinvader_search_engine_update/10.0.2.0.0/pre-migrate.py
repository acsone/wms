# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def migrate(cr, version):
    query = """ALTER table "shopinvader_variant" ALTER column "to_update"
            set data type varchar
            using case
        when "to_update" = true then 'true'
        when "to_update" = false then 'false'
        else null
    end;"""
    cr.execute(query)
