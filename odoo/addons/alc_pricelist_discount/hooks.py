# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def pre_init_hook(cr):
    """Fix data that does not follow the new constraints."""
    # Only Alcyon specific line:
    base_pl_ids = [2, 3, 67]  # prix de vente brut 1, 2, Alcyon France

    table = "product_pricelist"
    column = "is_discount"
    args = {"table": table, "column": column, "pl_ids": tuple(base_pl_ids)}
    if not column_exists(cr, table, column):
        # pylint: disable=sql-injection
        cr.execute('ALTER TABLE "%(table)s" ADD COLUMN "%(column)s" boolean;' % args)
        cr.execute(
            'ALTER TABLE "%(table)s" ALTER COLUMN "%(column)s" SET DEFAULT TRUE;' % args
        )
    # pylint: disable=sql-injection
    cr.execute("UPDATE %(table)s SET %(column)s = TRUE" % args)
    cr.execute("UPDATE %(table)s SET %(column)s = FALSE WHERE id IN %(pl_ids)s" % args)

    env = api.Environment(cr, SUPERUSER_ID, {})

    # delete remaining faulty pricelist properties, if any
    field = env.ref("product.field_res_partner_property_product_pricelist")
    value_references = ["product.pricelist,%s" % pl_id for pl_id in base_pl_ids]
    domain_bad_properties = [
        ("fields_id", "=", field.id),
        ("value_reference", "not in", value_references),
    ]
    env["ir.property"].search(domain_bad_properties).unlink()

    # remove faulty discount_pricelists
    domain_bad_partners = [("discount_pricelist_id", "in", base_pl_ids)]
    vals_partner = {"discount_pricelist_id": False}
    env["res.partner"].search(domain_bad_partners).write(vals_partner)
