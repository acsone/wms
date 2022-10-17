# -*- coding: utf-8 -*-
# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
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
