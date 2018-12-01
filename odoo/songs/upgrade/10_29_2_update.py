
# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from anthem.lyrics.records import add_xmlid

from ..common import req


@anthem.log
def set_not_print_flag_on_materiel_product(ctx):
    """Set the flag do not print label on materiel products"""
    categ_materiel = ctx.env.ref('specific_data.product_categ_materiel')

    products = ctx.env['product.template'].search([
        ('categ_id', 'child_of', categ_materiel.id)
    ])
    products.write({
        'is_do_not_print_label': True
    })
