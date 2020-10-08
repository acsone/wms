# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def pre_init_hook(cr):
    # avoid trouble with geoengine
    if column_exists(cr, "ir_ui_view", "projection"):
        cr.execute(
            "alter table ir_ui_view alter projection set " "default 'EPSG:900913';"
        )


def post_init_hook(cr, registry=None):
    cr.execute("update res_partner set manual_sale_order_allowed=customer")
    cr.execute(
        "update res_partner set customer=true where supplier=false "
        "and not parent_id is null"
    )
