# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """ Fix the value of applied_on for product price category.
    """
    cr.execute(
        "UPDATE product_pricelist_item set "
        "applied_on='2b_product_price_category' "
        "WHERE applied_on='4_product_price_category'"
    )
