# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute(
        "update product_template set description_shop_long=null, description_shop_short=null"
    )
    cr.execute(
        "delete from ir_translation where name = 'product.template,description_shop_short'"
    )
    cr.execute(
        "delete from ir_translation where name = 'product.template,description_shop_long'"
    )
