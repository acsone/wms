# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def uninstall_module_specific_translations(ctx):
    """ Uninstall the module specific_translations """

    # Uninstall the module specific_translation
    uninstall(ctx, ['specific_translations'])


@anthem.log
def _recompute_sale_order_line(ctx):
    """Recompute quantity remains to deliver as it is now a stored field"""
    ctx.env["sale.order.line"].search([
        ('state', 'in', ['sale'])
    ])._compute_product_qty_remains_to_deliver()


@anthem.log
def main(ctx):
    _recompute_sale_order_line(ctx)
    uninstall_module_specific_translations(ctx)
