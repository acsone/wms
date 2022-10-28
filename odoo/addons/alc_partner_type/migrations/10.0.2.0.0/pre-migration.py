# -*- coding: utf-8 -*-
# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return
    query_exists = """
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='product_template' AND column_name='allowed_partner_types'
    """
    cr.execute(query_exists)
    if cr.rowcount:
        return
    query_create = """
        ALTER TABLE product_template
        ADD COLUMN allowed_partner_types VARCHAR;
    """
    cr.execute(query_create)
    query_set = """
        UPDATE product_template
        SET allowed_partner_types = product_product.allowed_partner_types
        FROM product_product
        WHERE product_product.product_tmpl_id = product_template.id
    """
    cr.execute(query_set)
